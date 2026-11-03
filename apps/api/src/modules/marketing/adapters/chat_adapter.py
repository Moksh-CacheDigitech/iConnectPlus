"""OpenAI Chat Completions adapter for Marketing Chat (text + vision)."""

from __future__ import annotations

from typing import Any

import httpx

from core.config import settings
from modules.marketing.domain.exceptions import ValidationException


class ChatAdapter:
    def configured(self) -> bool:
        return bool(getattr(settings, "openai_api_key", "") and settings.openai_api_key.strip())

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        if not self.configured():
            raise ValidationException(
                "OpenAI is not configured. Set OPENAI_API_KEY on the API to use Marketing Chat."
            )
        if not messages:
            raise ValidationException("At least one chat message is required")

        key = settings.openai_api_key.strip()
        base = (getattr(settings, "openai_base_url", "") or "https://api.openai.com/v1").rstrip("/")
        resolved_model = (model or getattr(settings, "openai_model", "") or "gpt-4o-mini").strip()
        temp = max(0.0, min(2.0, float(temperature)))
        tokens = max(64, min(128000, int(max_tokens or 2048)))

        payload: dict[str, Any] = {
            "model": resolved_model,
            "temperature": temp,
            "messages": messages,
        }
        # Newer models prefer max_completion_tokens; fall back gracefully if rejected.
        payload["max_tokens"] = tokens

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                if response.status_code >= 400 and "max_tokens" in (response.text or "").lower():
                    payload.pop("max_tokens", None)
                    payload["max_completion_tokens"] = tokens
                    response = client.post(
                        f"{base}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {key}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )
            if response.status_code >= 400:
                raise ValidationException(f"OpenAI chat failed: {_extract_error(response)}")
            data = response.json()
        except ValidationException:
            raise
        except Exception as exc:
            raise ValidationException(f"OpenAI chat failed: {exc}") from exc

        choices = data.get("choices") if isinstance(data, dict) else None
        if not isinstance(choices, list) or not choices:
            raise ValidationException("OpenAI returned no chat choices")
        first = choices[0] if isinstance(choices[0], dict) else {}
        message = first.get("message") if isinstance(first.get("message"), dict) else {}
        content = str(message.get("content") or "").strip()
        if not content:
            raise ValidationException("OpenAI returned an empty assistant message")
        usage = data.get("usage") if isinstance(data, dict) else None
        return {
            "content": content,
            "model": str(data.get("model") or resolved_model),
            "usage": usage if isinstance(usage, dict) else None,
            "finish_reason": first.get("finish_reason"),
        }


def _extract_error(response: httpx.Response) -> str:
    try:
        body = response.json()
        err = body.get("error") if isinstance(body, dict) else None
        if isinstance(err, dict):
            return str(err.get("message") or err.get("code") or response.text)[:500]
        return str(body)[:500]
    except Exception:
        return (response.text or f"HTTP {response.status_code}")[:500]
