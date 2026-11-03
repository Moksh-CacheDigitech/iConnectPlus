"""OpenAI Images API adapter for marketing image posts."""

from __future__ import annotations

import base64
from typing import Any

import httpx

from core.config import settings
from modules.marketing.domain.exceptions import ValidationException

ALLOWED_SIZES = frozenset({"1024x1024", "1024x1536", "1536x1024"})
ALLOWED_QUALITIES = frozenset({"low", "medium", "high", "xhigh", "max", "auto"})
# Default to low — biggest cost lever; UI can raise quality for finals.
DEFAULT_QUALITY = "low"


class ImageGenAdapter:
    def configured(self) -> bool:
        return bool(getattr(settings, "openai_api_key", "") and settings.openai_api_key.strip())

    def generate(
        self,
        *,
        prompt: str,
        size: str = "1024x1024",
        quality: str = DEFAULT_QUALITY,
    ) -> dict[str, Any]:
        if not self.configured():
            raise ValidationException(
                "OpenAI is not configured. Set OPENAI_API_KEY on the API to generate image posts."
            )
        clean_prompt = (prompt or "").strip()
        if len(clean_prompt) < 8:
            raise ValidationException("Prompt must be at least 8 characters")
        if size not in ALLOWED_SIZES:
            raise ValidationException(
                f"Unsupported size {size!r}. Use one of: {', '.join(sorted(ALLOWED_SIZES))}"
            )
        quality_norm = (quality or DEFAULT_QUALITY).strip().lower() or DEFAULT_QUALITY
        if quality_norm not in ALLOWED_QUALITIES:
            raise ValidationException(
                f"Unsupported quality {quality!r}. Use one of: {', '.join(sorted(ALLOWED_QUALITIES))}"
            )
        quality = quality_norm

        key = settings.openai_api_key.strip()
        base = (getattr(settings, "openai_base_url", "") or "https://api.openai.com/v1").rstrip("/")
        model = (
            getattr(settings, "openai_image_model", "") or "gpt-image-2.5-flare"
        ).strip() or "gpt-image-2.5-flare"

        payload: dict[str, Any] = {
            "model": model,
            "prompt": clean_prompt,
            "size": size,
            "n": 1,
        }
        # gpt-image models accept quality; this is the main cost control (token count scales with quality).
        if model.startswith("gpt-image"):
            payload["quality"] = quality

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{base}/images/generations",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
            if response.status_code >= 400:
                detail = _extract_error(response)
                raise ValidationException(f"OpenAI image generation failed: {detail}")
            data = response.json()
        except ValidationException:
            raise
        except Exception as exc:
            raise ValidationException(f"OpenAI image generation failed: {exc}") from exc

        items = data.get("data") if isinstance(data, dict) else None
        if not isinstance(items, list) or not items:
            raise ValidationException("OpenAI returned no image data")
        first = items[0] if isinstance(items[0], dict) else {}
        b64 = first.get("b64_json")
        url = first.get("url")
        if b64:
            try:
                raw = base64.b64decode(b64)
            except Exception as exc:
                raise ValidationException("OpenAI returned invalid image payload") from exc
        elif url:
            raw = _download(url)
        else:
            raise ValidationException("OpenAI response missing image bytes")

        usage = data.get("usage") if isinstance(data, dict) else None
        resolved_quality = str(data.get("quality") or quality or "auto")
        return {
            "bytes": raw,
            "content_type": "image/png",
            "model": model,
            "size": size,
            "quality": resolved_quality,
            "usage": usage if isinstance(usage, dict) else None,
            "revised_prompt": first.get("revised_prompt"),
        }

    def edit(
        self,
        *,
        image_bytes: bytes,
        prompt: str,
        size: str = "1024x1024",
        quality: str = DEFAULT_QUALITY,
        content_type: str = "image/png",
    ) -> dict[str, Any]:
        """ChatGPT-style image edit: source image + new prompt → new image bytes."""
        if not self.configured():
            raise ValidationException(
                "OpenAI is not configured. Set OPENAI_API_KEY on the API to repurpose images."
            )
        clean_prompt = (prompt or "").strip()
        if len(clean_prompt) < 8:
            raise ValidationException("Repurpose prompt must be at least 8 characters")
        if not image_bytes:
            raise ValidationException("Source image bytes are required for repurpose")
        if size not in ALLOWED_SIZES:
            raise ValidationException(
                f"Unsupported size {size!r}. Use one of: {', '.join(sorted(ALLOWED_SIZES))}"
            )
        quality_norm = (quality or DEFAULT_QUALITY).strip().lower() or DEFAULT_QUALITY
        if quality_norm not in ALLOWED_QUALITIES:
            raise ValidationException(
                f"Unsupported quality {quality!r}. Use one of: {', '.join(sorted(ALLOWED_QUALITIES))}"
            )

        key = settings.openai_api_key.strip()
        base = (getattr(settings, "openai_base_url", "") or "https://api.openai.com/v1").rstrip("/")
        model = (
            getattr(settings, "openai_image_model", "") or "gpt-image-2.5-flare"
        ).strip() or "gpt-image-2.5-flare"

        # Multipart edits — keep filename extension aligned with content type.
        ext = "png"
        ctype = (content_type or "image/png").split(";")[0].strip().lower() or "image/png"
        if "jpeg" in ctype or "jpg" in ctype:
            ext = "jpg"
            ctype = "image/jpeg"
        elif "webp" in ctype:
            ext = "webp"
            ctype = "image/webp"

        form: dict[str, Any] = {
            "model": model,
            "prompt": clean_prompt,
            "size": size,
            "n": "1",
        }
        if model.startswith("gpt-image"):
            form["quality"] = quality_norm

        try:
            with httpx.Client(timeout=180.0) as client:
                response = client.post(
                    f"{base}/images/edits",
                    headers={"Authorization": f"Bearer {key}"},
                    data=form,
                    files={"image": (f"source.{ext}", image_bytes, ctype)},
                )
            if response.status_code >= 400:
                detail = _extract_error(response)
                raise ValidationException(f"OpenAI image edit failed: {detail}")
            data = response.json()
        except ValidationException:
            raise
        except Exception as exc:
            raise ValidationException(f"OpenAI image edit failed: {exc}") from exc

        items = data.get("data") if isinstance(data, dict) else None
        if not isinstance(items, list) or not items:
            raise ValidationException("OpenAI returned no edited image data")
        first = items[0] if isinstance(items[0], dict) else {}
        b64 = first.get("b64_json")
        url = first.get("url")
        if b64:
            try:
                raw = base64.b64decode(b64)
            except Exception as exc:
                raise ValidationException("OpenAI returned invalid edited image payload") from exc
        elif url:
            raw = _download(url)
        else:
            raise ValidationException("OpenAI edit response missing image bytes")

        usage = data.get("usage") if isinstance(data, dict) else None
        resolved_quality = str(data.get("quality") or quality_norm or "auto")
        return {
            "bytes": raw,
            "content_type": "image/png",
            "model": model,
            "size": size,
            "quality": resolved_quality,
            "usage": usage if isinstance(usage, dict) else None,
            "revised_prompt": first.get("revised_prompt"),
        }


def _download(url: str) -> bytes:
    with httpx.Client(timeout=120.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def _extract_error(response: httpx.Response) -> str:
    try:
        body = response.json()
        err = body.get("error") if isinstance(body, dict) else None
        if isinstance(err, dict):
            return str(err.get("message") or err.get("code") or response.text)[:500]
        return str(body)[:500]
    except Exception:
        return (response.text or f"HTTP {response.status_code}")[:500]
