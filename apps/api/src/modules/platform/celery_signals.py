"""Propagate request_id API → Celery worker and log task outcomes with it."""

from __future__ import annotations

import logging
import time

from celery.signals import before_task_publish, task_failure, task_postrun, task_prerun

from modules.platform.observability import get_request_id, set_request_id

logger = logging.getLogger("erp.platform.celery")

_HEADER = "x_request_id"
_started: dict[str, float] = {}


def _on_publish(headers: dict | None = None, **_: object) -> None:
    if headers is not None and _HEADER not in headers:
        request_id = get_request_id()
        if request_id:
            headers[_HEADER] = request_id


def _on_prerun(task_id: str | None = None, task=None, **_: object) -> None:
    request = getattr(task, "request", None)
    inherited = getattr(request, _HEADER, None) or (getattr(request, "headers", None) or {}).get(_HEADER)
    set_request_id(inherited or task_id)
    if task_id:
        _started[task_id] = time.perf_counter()


def _on_postrun(task_id: str | None = None, task=None, state: str | None = None, **_: object) -> None:
    started = _started.pop(task_id, None) if task_id else None
    logger.info(
        "task completed",
        extra={
            "task": getattr(task, "name", None),
            "task_id": task_id,
            "state": state,
            "duration_ms": round((time.perf_counter() - started) * 1000, 2) if started else None,
            "request_id": get_request_id(),
        },
    )


def _on_failure(task_id: str | None = None, exception: BaseException | None = None, sender=None, **_: object) -> None:
    logger.error(
        "task failed",
        extra={
            "task": getattr(sender, "name", None),
            "task_id": task_id,
            "error": repr(exception),
            "request_id": get_request_id(),
        },
    )


def install_celery_correlation() -> None:
    before_task_publish.connect(_on_publish, weak=False)
    task_prerun.connect(_on_prerun, weak=False)
    task_postrun.connect(_on_postrun, weak=False)
    task_failure.connect(_on_failure, weak=False)
