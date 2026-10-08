"""Idempotent Celery helpers (PY-06).

``system_job`` — scheduled, tenant-wide jobs: one successful run per job per
time window, claimed atomically so redelivery (``acks_late``) or overlapping
beat schedules cannot repeat business side effects.

``idempotent_task`` — tenant-scoped tasks keyed by an explicit idempotency key.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Literal, TypeVar
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from database.session import SessionLocal
from modules.platform.models.idempotency import FndIdempotencyRecord
from modules.platform.models.job_run import FndJobRun

F = TypeVar("F", bound=Callable[..., Any])

Window = Literal["hour", "day", "week"]

_WINDOW_FORMATS: dict[str, str] = {
    "hour": "%Y-%m-%dT%H",
    "day": "%Y-%m-%d",
    "week": "%G-W%V",
}


def window_key(window: Window, now: datetime | None = None) -> str:
    return (now or datetime.now(timezone.utc)).strftime(_WINDOW_FORMATS[window])


def _claim(job_name: str, key: str) -> bool:
    db = SessionLocal()
    try:
        stmt = (
            pg_insert(FndJobRun)
            .values(job_name=job_name, window_key=key, status="running")
            .on_conflict_do_nothing(constraint="uk_fnd_job_run_window")
            .returning(FndJobRun.id)
        )
        claimed = db.execute(stmt).scalar() is not None
        db.commit()
        return claimed
    finally:
        db.close()


def _finish(job_name: str, key: str, result: Any, *, ok: bool) -> None:
    db = SessionLocal()
    try:
        if ok:
            payload = result if isinstance(result, dict) else {"result": result}
            db.execute(
                update(FndJobRun)
                .where(FndJobRun.job_name == job_name, FndJobRun.window_key == key)
                .values(status="done", result_json=payload, finished_at=datetime.now(timezone.utc))
            )
        else:
            # Release the claim so a retry in the same window can run.
            db.execute(
                delete(FndJobRun).where(FndJobRun.job_name == job_name, FndJobRun.window_key == key)
            )
        db.commit()
    finally:
        db.close()


def system_job(job_name: str, *, window: Window = "day") -> Callable[[F], F]:
    """Run at most once per window. Pass ``idempotency_key=`` to force a specific window key."""

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, idempotency_key: str | None = None, **kwargs: Any) -> Any:
            key = idempotency_key or window_key(window)
            if not _claim(job_name, key):
                return {"status": "skipped", "reason": "already_ran", "window": key}
            try:
                result = fn(*args, **kwargs)
            except Exception:
                _finish(job_name, key, None, ok=False)
                raise
            _finish(job_name, key, result, ok=True)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def idempotent_task(
    *,
    scope: str,
    key_arg: str = "idempotency_key",
    tenant_arg: str = "tenant_id",
) -> Callable[[F], F]:
    """Skip re-execution when (tenant, scope, key) already stored."""

    def decorator(fn: F) -> F:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = kwargs.get(key_arg)
            tenant_raw = kwargs.get(tenant_arg)
            if not key or not tenant_raw:
                return fn(*args, **kwargs)

            tenant_id = UUID(str(tenant_raw))
            db = SessionLocal()
            try:
                stmt = select(FndIdempotencyRecord).where(
                    FndIdempotencyRecord.tenant_id == tenant_id,
                    FndIdempotencyRecord.scope == scope,
                    FndIdempotencyRecord.idempotency_key == str(key),
                )
                existing = db.scalars(stmt).first()
                if existing is not None:
                    return existing.result_json

                result = fn(*args, **kwargs)
                payload = result if isinstance(result, dict) else {"result": result}
                db.add(
                    FndIdempotencyRecord(
                        tenant_id=tenant_id,
                        scope=scope,
                        idempotency_key=str(key),
                        result_json=payload,
                    )
                )
                db.commit()
                return result
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

        return wrapper  # type: ignore[return-value]

    return decorator
