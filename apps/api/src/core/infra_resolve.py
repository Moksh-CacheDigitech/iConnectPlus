"""Prefer VM infrastructure; fall back to local Docker when unreachable.

Primary (VM) URLs stay authoritative. When the VM is reachable we always keep
settings pointed at those URLs so the process stays synced with VM services.
Local fallbacks apply only while the primary Postgres probe fails.
"""

from __future__ import annotations

import socket
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from core.config import Settings

# Set by apply_infra_fallback — "primary" | "fallback"
ACTIVE_INFRA_SOURCE = "primary"

# Snapshot of primary URLs taken before any fallback mutation.
_PRIMARY_URLS: dict[str, str] = {}


def _tcp_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _host_port_from_url(url: str, default_port: int) -> tuple[str, int] | None:
    raw = (url or "").strip()
    if not raw:
        return None
    if "://" not in raw:
        raw = f"tcp://{raw}"
    parsed = urlparse(raw)
    host = parsed.hostname
    if not host:
        return None
    port = parsed.port or default_port
    return host, port


def _snapshot_primaries(settings: Settings) -> None:
    """Capture VM/primary URLs once so we can restore when the VM returns."""
    global _PRIMARY_URLS
    if _PRIMARY_URLS:
        return
    _PRIMARY_URLS = {
        "database_url": str(settings.database_url),
        "redis_url": settings.redis_url,
        "celery_broker_url": settings.celery_broker_url,
        "celery_result_backend": settings.celery_result_backend,
        "s3_endpoint_url": settings.s3_endpoint_url,
        "opensearch_url": settings.opensearch_url,
    }


def _restore_primaries(settings: Settings) -> None:
    if not _PRIMARY_URLS:
        return
    settings.database_url = _PRIMARY_URLS["database_url"]
    settings.redis_url = _PRIMARY_URLS["redis_url"]
    settings.celery_broker_url = _PRIMARY_URLS["celery_broker_url"]
    settings.celery_result_backend = _PRIMARY_URLS["celery_result_backend"]
    settings.s3_endpoint_url = _PRIMARY_URLS["s3_endpoint_url"]
    settings.opensearch_url = _PRIMARY_URLS["opensearch_url"]


def primary_infra_reachable(settings: Settings, timeout: float = 2.0) -> bool:
    """True when primary (VM) Postgres accepts TCP — gate for the whole primary set."""
    primary_db = (_PRIMARY_URLS.get("database_url") if _PRIMARY_URLS else None) or str(
        settings.database_url
    )
    db = _host_port_from_url(primary_db, 5432)
    if not db:
        return False
    return _tcp_reachable(db[0], db[1], timeout=timeout)


def apply_infra_fallback(settings: Settings) -> str:
    """
    Keep settings on VM primary when reachable; otherwise apply local Docker fallbacks.

    Returns the active source: ``primary`` or ``fallback``.
    Safe to call more than once — restores primary URLs when the VM comes back.
    """
    global ACTIVE_INFRA_SOURCE

    _snapshot_primaries(settings)

    if not settings.infra_fallback_enabled:
        _restore_primaries(settings)
        ACTIVE_INFRA_SOURCE = "primary"
        return ACTIVE_INFRA_SOURCE

    has_fallback = bool(
        (settings.database_url_fallback or "").strip()
        or (settings.redis_url_fallback or "").strip()
    )
    if not has_fallback:
        _restore_primaries(settings)
        ACTIVE_INFRA_SOURCE = "primary"
        return ACTIVE_INFRA_SOURCE

    if primary_infra_reachable(settings):
        _restore_primaries(settings)
        ACTIVE_INFRA_SOURCE = "primary"
        return ACTIVE_INFRA_SOURCE

    # Switch each configured fallback independently (blank = keep primary value).
    if (settings.database_url_fallback or "").strip():
        settings.database_url = settings.database_url_fallback.strip()
    if (settings.redis_url_fallback or "").strip():
        settings.redis_url = settings.redis_url_fallback.strip()
    if (settings.celery_broker_url_fallback or "").strip():
        settings.celery_broker_url = settings.celery_broker_url_fallback.strip()
    if (settings.celery_result_backend_fallback or "").strip():
        settings.celery_result_backend = settings.celery_result_backend_fallback.strip()
    if (settings.s3_endpoint_url_fallback or "").strip():
        settings.s3_endpoint_url = settings.s3_endpoint_url_fallback.strip()
    if (settings.opensearch_url_fallback or "").strip():
        settings.opensearch_url = settings.opensearch_url_fallback.strip()

    ACTIVE_INFRA_SOURCE = "fallback"
    return ACTIVE_INFRA_SOURCE


__all__ = [
    "ACTIVE_INFRA_SOURCE",
    "apply_infra_fallback",
    "primary_infra_reachable",
]
