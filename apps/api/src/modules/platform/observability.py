"""Correlation / structured log helpers and in-process SLO sample window."""

from __future__ import annotations

import logging
import threading
from collections import deque
from contextvars import ContextVar
from uuid import uuid4

_request_id: ContextVar[str | None] = ContextVar("platform_request_id", default=None)
logger = logging.getLogger("erp.platform")

# Per-process rolling window; each API/worker process reports its own samples.
_SAMPLE_WINDOW = 2000
_samples: dict[str, deque[tuple[float, bool]]] = {}
_lock = threading.Lock()


def set_request_id(request_id: str | None = None) -> str:
    value = request_id or str(uuid4())
    _request_id.set(value)
    return value


def get_request_id() -> str | None:
    return _request_id.get()


def log_path_metric(path_key: str, *, latency_ms: float, success: bool) -> None:
    with _lock:
        _samples.setdefault(path_key, deque(maxlen=_SAMPLE_WINDOW)).append((latency_ms, success))
    logger.info(
        "slo_sample",
        extra={
            "path_key": path_key,
            "latency_ms": round(latency_ms, 2),
            "success": success,
            "request_id": get_request_id(),
        },
    )


def path_samples(path_key: str) -> list[tuple[float, bool]]:
    with _lock:
        return list(_samples.get(path_key, ()))
