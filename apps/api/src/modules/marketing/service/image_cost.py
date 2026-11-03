"""OpenAI GPT Image cost helpers (token rates → USD)."""

from __future__ import annotations

from typing import Any

# Standard processing rates for gpt-image-2.5-flare / sunburst (USD per 1M tokens).
TEXT_INPUT_PER_M = 5.0
IMAGE_INPUT_PER_M = 8.0
IMAGE_OUTPUT_PER_M = 30.0

# Budgeting estimates for output image tokens when API usage is missing.
# Source: published GPT Image 2.5 planning tables (output-only).
ESTIMATED_OUTPUT_TOKENS: dict[str, dict[str, int]] = {
    "1024x1024": {"low": 196, "medium": 439, "high": 1756, "xhigh": 3122, "max": 7024, "auto": 439},
    "1024x1536": {"low": 158, "medium": 343, "high": 1372, "xhigh": 2459, "max": 5488, "auto": 343},
    "1536x1024": {"low": 158, "medium": 343, "high": 1372, "xhigh": 2459, "max": 5488, "auto": 343},
}


def usd_from_tokens(*, text_in: int = 0, image_in: int = 0, image_out: int = 0) -> float:
    return round(
        (max(0, text_in) * TEXT_INPUT_PER_M / 1_000_000)
        + (max(0, image_in) * IMAGE_INPUT_PER_M / 1_000_000)
        + (max(0, image_out) * IMAGE_OUTPUT_PER_M / 1_000_000),
        6,
    )


def cost_from_usage(usage: dict[str, Any] | None, *, model: str, size: str, quality: str) -> dict[str, Any]:
    """Build a persisted cost block from OpenAI `usage` (preferred) or size/quality estimate."""
    if isinstance(usage, dict) and usage:
        details_in = usage.get("input_tokens_details") if isinstance(usage.get("input_tokens_details"), dict) else {}
        details_out = usage.get("output_tokens_details") if isinstance(usage.get("output_tokens_details"), dict) else {}
        text_in = int(details_in.get("text_tokens") or 0)
        image_in = int(details_in.get("image_tokens") or 0)
        image_out = int(details_out.get("image_tokens") or usage.get("output_tokens") or 0)
        total = int(usage.get("total_tokens") or (text_in + image_in + image_out))
        usd = usd_from_tokens(text_in=text_in, image_in=image_in, image_out=image_out)
        return {
            "source": "api_usage",
            "model": model,
            "size": size,
            "quality": quality,
            "text_input_tokens": text_in,
            "image_input_tokens": image_in,
            "image_output_tokens": image_out,
            "total_tokens": total,
            "usd": usd,
            "currency": "USD",
            "rates": {
                "text_input_per_m": TEXT_INPUT_PER_M,
                "image_input_per_m": IMAGE_INPUT_PER_M,
                "image_output_per_m": IMAGE_OUTPUT_PER_M,
            },
        }

    q = (quality or "auto").lower()
    size_map = ESTIMATED_OUTPUT_TOKENS.get(size) or ESTIMATED_OUTPUT_TOKENS["1024x1024"]
    image_out = int(size_map.get(q) or size_map["auto"])
    # Rough prompt budget when usage missing (~4 chars/token).
    text_in = 20
    usd = usd_from_tokens(text_in=text_in, image_out=image_out)
    return {
        "source": "estimate",
        "model": model,
        "size": size,
        "quality": quality,
        "text_input_tokens": text_in,
        "image_input_tokens": 0,
        "image_output_tokens": image_out,
        "total_tokens": text_in + image_out,
        "usd": usd,
        "currency": "USD",
        "rates": {
            "text_input_per_m": TEXT_INPUT_PER_M,
            "image_input_per_m": IMAGE_INPUT_PER_M,
            "image_output_per_m": IMAGE_OUTPUT_PER_M,
        },
    }


def format_usd(value: float | None) -> str:
    if value is None:
        return "$0.00"
    if value < 0.01:
        return f"${value:.4f}"
    return f"${value:.2f}"
