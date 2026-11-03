"""Frankfurter FX — free lifetime USD→INR (no API key).

Public API: https://api.frankfurter.dev
Docs: https://frankfurter.dev/
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx
from redis.exceptions import RedisError

from core.config import settings
from core.redis import get_redis

logger = logging.getLogger(__name__)

_CACHE_KEY = "fx:frankfurter:USD:INR"
_MEMORY: dict[str, Any] = {"payload": None, "expires_at": 0.0}


def get_usd_inr_rate(*, force_refresh: bool = False) -> dict[str, Any]:
    """Return USD→INR mid rate with source metadata (cached ~12h).

    Pass force_refresh=True when the Marketing Content Studio mounts so the
    user sees today's Frankfurter reference rate once per visit.
    """
    stale: dict[str, Any] | None = None
    if force_refresh:
        stale = _read_cache()
        _clear_cache()
    else:
        cached = _read_cache()
        if cached is not None:
            return cached

    fetched = _fetch_frankfurter()
    if fetched is not None:
        _write_cache(fetched)
        return fetched

    # Forced refresh failed — keep last good rate if we had one.
    if stale is not None:
        _write_cache(stale)
        return stale

    return {
        "usd_inr": float(settings.frankfurter_fallback_usd_inr),
        "as_of": None,
        "source": "fallback",
        "provider": "frankfurter",
        "provider_url": settings.frankfurter_base_url.rstrip("/"),
    }


def _clear_cache() -> None:
    _MEMORY["payload"] = None
    _MEMORY["expires_at"] = 0.0
    try:
        get_redis().delete(_CACHE_KEY)
    except RedisError as exc:
        logger.warning("Redis unavailable for Frankfurter FX cache clear: %s", exc)


def _read_cache() -> dict[str, Any] | None:
    now = time.time()
    mem = _MEMORY.get("payload")
    if isinstance(mem, dict) and float(_MEMORY.get("expires_at") or 0) > now:
        return mem

    try:
        raw = get_redis().get(_CACHE_KEY)
    except RedisError as exc:
        logger.warning("Redis unavailable for Frankfurter FX cache read: %s", exc)
        return None
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or data.get("usd_inr") is None:
        return None
    ttl = int(settings.frankfurter_cache_ttl_seconds)
    _MEMORY["payload"] = data
    _MEMORY["expires_at"] = now + ttl
    return data


def _write_cache(payload: dict[str, Any]) -> None:
    ttl = max(60, int(settings.frankfurter_cache_ttl_seconds))
    _MEMORY["payload"] = payload
    _MEMORY["expires_at"] = time.time() + ttl
    try:
        get_redis().setex(_CACHE_KEY, ttl, json.dumps(payload))
    except RedisError as exc:
        logger.warning("Redis unavailable for Frankfurter FX cache write: %s", exc)


def _fetch_frankfurter() -> dict[str, Any] | None:
    if not settings.frankfurter_enabled:
        return None

    base = settings.frankfurter_base_url.rstrip("/")
    url = f"{base}/v2/rates"
    try:
        with httpx.Client(timeout=8.0) as client:
            response = client.get(url, params={"base": "USD", "quotes": "INR"})
            response.raise_for_status()
            body = response.json()
    except Exception as exc:  # noqa: BLE001 — network/parse; fall back
        logger.warning("Frankfurter FX fetch failed: %s", exc)
        return None

    rate, as_of = _parse_rate(body)
    if rate is None or rate <= 0:
        logger.warning("Frankfurter FX response missing USD/INR rate: %s", body)
        return None

    return {
        "usd_inr": round(float(rate), 4),
        "as_of": as_of,
        "source": "frankfurter",
        "provider": "frankfurter",
        "provider_url": base,
    }


def _parse_rate(body: Any) -> tuple[float | None, str | None]:
    """Support v2 list payload and legacy object shapes."""
    if isinstance(body, list) and body:
        row = body[0]
        if isinstance(row, dict):
            rate = row.get("rate")
            as_of = row.get("date")
            try:
                return float(rate), str(as_of) if as_of else None
            except (TypeError, ValueError):
                return None, None

    if isinstance(body, dict):
        rates = body.get("rates")
        as_of = body.get("date")
        if isinstance(rates, dict) and rates.get("INR") is not None:
            try:
                return float(rates["INR"]), str(as_of) if as_of else None
            except (TypeError, ValueError):
                return None, None

    return None, None
