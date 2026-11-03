"""Canva Connect adapter — OAuth PKCE, asset upload, Magic Layers image-to-design."""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx

from core.config import settings
from core.redis import SessionStore
from modules.marketing.domain.exceptions import ValidationException

CANVA_AUTH_URL = "https://www.canva.com/api/oauth/authorize"
CANVA_TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"
CANVA_API = "https://api.canva.com/rest/v1"
DEFAULT_SCOPES = "asset:read asset:write design:content:write design:meta:read"


class CanvaAdapter:
    def __init__(self, store: SessionStore | None = None) -> None:
        self._store = store or SessionStore()

    def configured(self) -> bool:
        return bool(
            (settings.canva_client_id or "").strip()
            and (settings.canva_client_secret or "").strip()
            and (settings.canva_redirect_uri or "").strip()
        )

    def status(self, user_id: UUID) -> dict[str, Any]:
        tokens = self._get_tokens(user_id)
        return {
            "configured": self.configured(),
            "connected": bool(tokens and tokens.get("access_token")),
            "scopes": (settings.canva_scopes or DEFAULT_SCOPES).strip(),
        }

    def build_authorize_url(self, *, user_id: UUID, return_to: str | None = None) -> dict[str, str]:
        if not self.configured():
            raise ValidationException(
                "Canva is not configured. Set CANVA_CLIENT_ID, CANVA_CLIENT_SECRET, "
                "and CANVA_REDIRECT_URI on the API."
            )
        verifier = _pkce_verifier()
        challenge = _pkce_challenge(verifier)
        state = secrets.token_urlsafe(24)
        self._store.set_oauth_state(
            state,
            {
                "provider": "canva",
                "user_id": str(user_id),
                "code_verifier": verifier,
                "return_to": (return_to or "").strip() or "/marketing/content",
            },
            ttl_seconds=1800,
        )
        params = {
            "code_challenge": challenge,
            "code_challenge_method": "S256",
            "response_type": "code",
            "client_id": settings.canva_client_id.strip(),
            "redirect_uri": settings.canva_redirect_uri.strip(),
            "scope": (settings.canva_scopes or DEFAULT_SCOPES).strip(),
            "state": state,
        }
        return {"authorize_url": f"{CANVA_AUTH_URL}?{urlencode(params)}", "state": state}

    def exchange_code(self, *, code: str, state: str) -> dict[str, Any]:
        if not self.configured():
            raise ValidationException("Canva is not configured")

        # React Strict Mode / double-callback: return the first successful exchange.
        cached = self._store.get_oauth_exchange(f"canva:{state}")
        if cached and cached.get("connected"):
            return cached

        payload = self._store.pop_oauth_state_atomic(state)
        if not payload or payload.get("provider") != "canva":
            # Race: sibling request may have finished while we lost the state pop.
            cached = self._store.get_oauth_exchange(f"canva:{state}")
            if cached and cached.get("connected"):
                return cached
            raise ValidationException(
                "Canva OAuth state is invalid or expired. Try Connect again."
            )
        verifier = payload.get("code_verifier")
        user_id = payload.get("user_id")
        if not verifier or not user_id:
            raise ValidationException("Canva OAuth state is incomplete")

        token = self._token_request(
            {
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": settings.canva_redirect_uri.strip(),
            }
        )
        self._save_tokens(UUID(str(user_id)), token)
        result = {
            "connected": True,
            "return_to": payload.get("return_to") or "/marketing/content",
            "user_id": str(user_id),
        }
        self._store.set_oauth_exchange(f"canva:{state}", result, ttl_seconds=600)
        return result

    def ensure_access_token(self, user_id: UUID, *, force_refresh: bool = False) -> str:
        tokens = self._get_tokens(user_id)
        if not tokens or not tokens.get("access_token"):
            raise ValidationException(
                "Canva is not connected for this user. Click Connect Canva first."
            )
        expires_at = float(tokens.get("expires_at") or 0)
        if not force_refresh and expires_at > time.time() + 60:
            return str(tokens["access_token"])
        refresh = tokens.get("refresh_token")
        if not refresh:
            self._clear_tokens(user_id)
            raise ValidationException("Canva session expired. Connect Canva again.")
        try:
            refreshed = self._token_request(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh,
                }
            )
        except ValidationException:
            self._clear_tokens(user_id)
            raise ValidationException("Canva session expired. Connect Canva again.") from None
        self._save_tokens(user_id, refreshed)
        return str(refreshed["access_token"])

    def upload_image(
        self,
        *,
        user_id: UUID,
        image_bytes: bytes,
        name: str,
    ) -> str:
        safe_name = (name or "marketing-image")[:50]
        name_b64 = base64.b64encode(safe_name.encode("utf-8")).decode("ascii")

        def _attempt(access: str) -> str:
            headers = {
                "Authorization": f"Bearer {access}",
                "Content-Type": "application/octet-stream",
                "Asset-Upload-Metadata": json.dumps({"name_base64": name_b64}),
            }
            with httpx.Client(timeout=120.0) as client:
                start = client.post(
                    f"{CANVA_API}/asset-uploads",
                    headers=headers,
                    content=image_bytes,
                )
                if start.status_code >= 400:
                    raise _CanvaHttpError(start.status_code, _err(start))
                job = (start.json() or {}).get("job") or {}
                job_id = job.get("id")
                if not job_id:
                    raise ValidationException("Canva upload did not return a job id")
                return self._poll_asset_job(client, access, str(job_id))

        return self._auth_retry(user_id, "Canva upload failed", _attempt)

    def image_to_design(
        self,
        *,
        user_id: UUID,
        asset_id: str,
        title: str,
    ) -> dict[str, Any]:
        """Convert a flat image into an editable Canva design (Magic Layers)."""
        body = {
            "image": {"asset_id": asset_id},
            "title": (title or "Marketing image post")[:255],
        }

        def _attempt(access: str) -> dict[str, Any]:
            with httpx.Client(timeout=120.0) as client:
                start = client.post(
                    f"{CANVA_API}/image-to-design-imports",
                    headers={
                        "Authorization": f"Bearer {access}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                if start.status_code == 429:
                    raise ValidationException(
                        "Canva AI credit quota exceeded. Try again later or use Create design (flat)."
                    )
                if start.status_code >= 400:
                    if _is_auth_failure(start.status_code, _err(start)):
                        raise _CanvaHttpError(start.status_code, _err(start))
                    return self.create_flat_design(
                        user_id=user_id,
                        asset_id=asset_id,
                        title=title,
                        reason=_err(start),
                    )
                job = (start.json() or {}).get("job") or {}
                job_id = job.get("id")
                if not job_id:
                    return self.create_flat_design(
                        user_id=user_id,
                        asset_id=asset_id,
                        title=title,
                        reason="missing image-to-design job id",
                    )
                try:
                    result = self._poll_image_to_design(client, access, str(job_id))
                    result["canva_asset_id"] = asset_id
                    return result
                except ValidationException as exc:
                    msg = str(exc)
                    if msg.startswith("CANVA_MAGIC_LAYERS_FAILED:"):
                        return self.create_flat_design(
                            user_id=user_id,
                            asset_id=asset_id,
                            title=title,
                            reason=msg.split(":", 2)[-1],
                        )
                    raise

        return self._auth_retry(user_id, "Canva Magic Layers failed", _attempt)

    def create_flat_design(
        self,
        *,
        user_id: UUID,
        asset_id: str,
        title: str,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Place the image into a new design as a single asset (no Magic Layers)."""
        payload = {
            "design_type": {"type": "preset", "name": "instagram_post"},
            "asset_id": asset_id,
            "title": (title or "Marketing image post")[:255],
        }

        def _attempt(access: str) -> dict[str, Any]:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{CANVA_API}/designs",
                    headers={
                        "Authorization": f"Bearer {access}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if response.status_code >= 400:
                    raise _CanvaHttpError(response.status_code, _err(response))
                design = (response.json() or {}).get("design") or {}
            edit_url = ((design.get("urls") or {}).get("edit_url")) or design.get("url")
            if not edit_url:
                design_id = design.get("id")
                if design_id:
                    edit_url = f"https://www.canva.com/design/{design_id}/edit"
            if not edit_url:
                raise ValidationException("Canva did not return an edit URL")
            return {
                "mode": "flat_asset",
                "fallback_reason": reason,
                "canva_asset_id": asset_id,
                "canva_design_id": design.get("id"),
                "canva_edit_url": edit_url,
                "canva_view_url": ((design.get("urls") or {}).get("view_url")),
            }

        try:
            return self._auth_retry(user_id, "Canva design create failed", _attempt)
        except ValidationException as exc:
            if reason:
                raise ValidationException(f"{exc} (after Magic Layers: {reason})") from None
            raise

    def _poll_asset_job(self, client: httpx.Client, access: str, job_id: str) -> str:
        for _ in range(40):
            response = client.get(
                f"{CANVA_API}/asset-uploads/{job_id}",
                headers={"Authorization": f"Bearer {access}"},
            )
            if response.status_code >= 400:
                detail = _err(response)
                if _is_auth_failure(response.status_code, detail):
                    raise _CanvaHttpError(response.status_code, detail)
                raise ValidationException(f"Canva upload poll failed: {detail}")
            job = (response.json() or {}).get("job") or {}
            status = job.get("status")
            if status == "success":
                asset = job.get("asset") or {}
                asset_id = asset.get("id")
                if not asset_id:
                    raise ValidationException("Canva upload succeeded without asset id")
                return str(asset_id)
            if status == "failed":
                err = job.get("error") or {}
                detail = str(err.get("message") or err.get("code") or "unknown")
                if _is_auth_failure(401, detail):
                    raise _CanvaHttpError(401, detail)
                raise ValidationException(f"Canva upload failed: {detail}")
            time.sleep(1.0)
        raise ValidationException("Canva upload timed out")

    def _poll_image_to_design(
        self,
        client: httpx.Client,
        access: str,
        job_id: str,
    ) -> dict[str, Any]:
        for _ in range(60):
            response = client.get(
                f"{CANVA_API}/image-to-design-imports/{job_id}",
                headers={"Authorization": f"Bearer {access}"},
            )
            if response.status_code >= 400:
                raise ValidationException(
                    f"CANVA_MAGIC_LAYERS_FAILED:poll:{_err(response)}"
                )

            job = (response.json() or {}).get("job") or {}
            status = job.get("status")
            if status == "success":
                design = ((job.get("result") or {}).get("design")) or {}
                urls = design.get("urls") or {}
                design_id = design.get("id")
                edit_url = urls.get("edit_url") or (
                    f"https://www.canva.com/design/{design_id}/edit" if design_id else None
                )
                if not edit_url:
                    raise ValidationException("Canva Magic Layers returned no edit URL")
                return {
                    "mode": "magic_layers",
                    "canva_design_id": design_id,
                    "canva_edit_url": edit_url,
                    "canva_view_url": urls.get("view_url"),
                }
            if status == "failed":
                err = job.get("error") or {}
                raise ValidationException(
                    f"CANVA_MAGIC_LAYERS_FAILED:{err.get('code') or 'failed'}:"
                    f"{err.get('message') or 'Magic Layers failed'}"
                )
            time.sleep(1.5)
        raise ValidationException("CANVA_MAGIC_LAYERS_FAILED:timeout:Canva Magic Layers timed out")

    def _auth_retry(self, user_id: UUID, label: str, attempt):
        """Run an authenticated Canva call; refresh+retry once on revoked/401 tokens."""
        access = self.ensure_access_token(user_id)
        try:
            return attempt(access)
        except _CanvaHttpError as exc:
            if not _is_auth_failure(exc.status_code, exc.message):
                raise ValidationException(f"{label}: {exc.message}") from None
            # Access token may still look fresh locally but Canva has revoked it.
            access = self.ensure_access_token(user_id, force_refresh=True)
            try:
                return attempt(access)
            except _CanvaHttpError as retry_exc:
                if _is_auth_failure(retry_exc.status_code, retry_exc.message):
                    self._clear_tokens(user_id)
                    raise ValidationException(
                        "Canva session expired. Connect Canva again."
                    ) from None
                raise ValidationException(f"{label}: {retry_exc.message}") from None

    def _token_request(self, form: dict[str, str]) -> dict[str, Any]:
        client_id = settings.canva_client_id.strip()
        client_secret = settings.canva_client_secret.strip()
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode("ascii")
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                CANVA_TOKEN_URL,
                headers={
                    "Authorization": f"Basic {basic}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data=form,
            )
        if response.status_code >= 400:
            raise ValidationException(f"Canva token exchange failed: {_err(response)}")
        data = response.json()
        if not isinstance(data, dict) or not data.get("access_token"):
            raise ValidationException("Canva token response missing access_token")
        return data

    def _save_tokens(self, user_id: UUID, token: dict[str, Any]) -> None:
        expires_in = int(token.get("expires_in") or 14400)
        existing = self._get_tokens(user_id) or {}
        # Canva may omit refresh_token on refresh; keep the previous one.
        refresh = token.get("refresh_token") or existing.get("refresh_token")
        payload = {
            "access_token": token.get("access_token"),
            "refresh_token": refresh,
            "token_type": token.get("token_type") or "Bearer",
            "scope": token.get("scope") or existing.get("scope"),
            "expires_at": time.time() + max(60, expires_in),
        }
        try:
            self._store._client.setex(  # noqa: SLF001 — intentional token vault
                f"canva:tokens:{user_id}",
                # Keep refresh token available beyond short access TTL (60 days).
                max(expires_in + 86_400, 60 * 86_400),
                json.dumps(payload),
            )
        except Exception as exc:
            raise ValidationException(f"Could not store Canva tokens: {exc}") from exc

    def _get_tokens(self, user_id: UUID) -> dict[str, Any] | None:
        try:
            raw = self._store._client.get(f"canva:tokens:{user_id}")  # noqa: SLF001
            if not raw:
                return None
            data = json.loads(raw)
            return data if isinstance(data, dict) else None
        except Exception:
            return None

    def _clear_tokens(self, user_id: UUID) -> None:
        try:
            self._store._client.delete(f"canva:tokens:{user_id}")  # noqa: SLF001
        except Exception:
            pass


class _CanvaHttpError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def _is_auth_failure(status_code: int, message: str) -> bool:
    if status_code in {401, 403}:
        return True
    text = (message or "").lower()
    return any(
        needle in text
        for needle in (
            "revoked",
            "invalid_token",
            "invalid token",
            "expired",
            "unauthorized",
            "access token",
            "not authorized",
        )
    )


def _pkce_verifier() -> str:
    return secrets.token_urlsafe(64)[:128]


def _pkce_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _err(response: httpx.Response) -> str:
    try:
        body = response.json()
        if isinstance(body, dict):
            return str(body.get("message") or body.get("code") or body)[:500]
        return str(body)[:500]
    except Exception:
        return (response.text or f"HTTP {response.status_code}")[:500]
