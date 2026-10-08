"""Platform Celery tasks — outbox drain + retention purge."""

import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from database.session import SessionLocal
from modules.platform.celery_idempotent import system_job
from modules.platform.models.idempotency import FndIdempotencyRecord
from modules.platform.models.job_run import FndJobRun
from modules.platform.models.outbox import FndOutboxMessage
from modules.platform.observability import log_path_metric
from modules.platform.retention import purge_cutoff
from workers.celery_app import celery_app

_IDEMPOTENCY_RETENTION_DAYS = 30
_JOB_RUN_RETENTION_DAYS = 90


@celery_app.task(name="platform.outbox_drain")
def outbox_drain_task(limit: int = 50) -> dict:
    from modules.platform.outbox.dispatcher import OutboxDispatcher

    started = time.perf_counter()
    db = SessionLocal()
    try:
        result = OutboxDispatcher(db).process_batch(limit=limit)
    finally:
        db.close()
    log_path_metric(
        "outbox.drain",
        latency_ms=(time.perf_counter() - started) * 1000,
        success=result.get("failed", 0) == 0,
    )
    return result


@celery_app.task(name="platform.outbox_purge")
@system_job("platform.outbox_purge", window="day")
def outbox_purge_task() -> dict:
    """Purge processed outbox rows past retention."""
    cutoff = purge_cutoff("outbox_processed")
    db = SessionLocal()
    try:
        result = db.execute(
            delete(FndOutboxMessage).where(
                FndOutboxMessage.status == "processed",
                FndOutboxMessage.created_at < cutoff,
            )
        )
        db.commit()
        return {"purged": result.rowcount or 0, "cutoff": cutoff.isoformat()}
    finally:
        db.close()


@celery_app.task(name="platform.retention_purge")
@system_job("platform.retention_purge", window="day")
def retention_purge_task() -> dict:
    """Purge expired idempotency keys, job-run claims and delivered notifications."""
    from modules.foundation.models.notification import NtfDelivery, NtfEvent

    now = datetime.now(timezone.utc)
    db = SessionLocal()
    try:
        idem = db.execute(
            delete(FndIdempotencyRecord).where(
                FndIdempotencyRecord.created_at < now - timedelta(days=_IDEMPOTENCY_RETENTION_DAYS)
            )
        ).rowcount
        runs = db.execute(
            delete(FndJobRun).where(
                FndJobRun.started_at < now - timedelta(days=_JOB_RUN_RETENTION_DAYS)
            )
        ).rowcount
        expired_events = select(NtfEvent.id).where(
            NtfEvent.status.in_(("sent", "delivered", "read")),
            NtfEvent.created_at < purge_cutoff("notification"),
        )
        db.execute(delete(NtfDelivery).where(NtfDelivery.event_id.in_(expired_events)))
        notifications = db.execute(delete(NtfEvent).where(NtfEvent.id.in_(expired_events))).rowcount
        db.commit()
        return {
            "idempotency_purged": idem or 0,
            "job_runs_purged": runs or 0,
            "notifications_purged": notifications or 0,
        }
    finally:
        db.close()
