"""Chat completion + image-in-chat cost helpers (token rates → USD)."""

from __future__ import annotations

from typing import Any

from modules.marketing.service.image_cost import cost_from_usage as image_cost_from_usage

# Published OpenAI chat rates (USD per 1M tokens) — approximate public list prices.
CHAT_RATES: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.0),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1": (2.00, 8.0),
    "o4-mini": (1.10, 4.40),
}
DEFAULT_CHAT_RATES = (0.15, 0.60)  # gpt-4o-mini


def _rates_for_model(model: str | None) -> tuple[float, float]:
    key = (model or "").strip().lower()
    if not key:
        return DEFAULT_CHAT_RATES
    for prefix, rates in CHAT_RATES.items():
        if key.startswith(prefix):
            return rates
    return DEFAULT_CHAT_RATES


def _is_image_usage(usage: dict[str, Any]) -> bool:
    if "input_tokens_details" in usage or "output_tokens_details" in usage:
        return True
    if "input_tokens" in usage and "prompt_tokens" not in usage:
        return True
    return False


def cost_from_chat_usage(
    usage: dict[str, Any] | None,
    *,
    model: str | None = None,
    size: str = "1024x1024",
    quality: str = "auto",
) -> dict[str, Any] | None:
    """Build a cost block from assistant message usage_json (chat or image)."""
    if not isinstance(usage, dict) or not usage:
        return None

    if _is_image_usage(usage):
        block = image_cost_from_usage(usage, model=model or "gpt-image", size=size, quality=quality)
        block["kind"] = "image"
        return block

    prompt = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    completion = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    total = int(usage.get("total_tokens") or (prompt + completion))
    if total <= 0 and prompt <= 0 and completion <= 0:
        return None

    in_rate, out_rate = _rates_for_model(model)
    usd = round((prompt * in_rate / 1_000_000) + (completion * out_rate / 1_000_000), 6)
    return {
        "usd": usd,
        "total_tokens": total,
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "source": "api_usage",
        "model": model,
        "kind": "chat",
        "rates": {
            "input_per_m": in_rate,
            "output_per_m": out_rate,
        },
    }
