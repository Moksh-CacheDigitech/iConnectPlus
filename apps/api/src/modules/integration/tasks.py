"""Integration Celery task stubs per ERD_21 section 11."""

from workers.celery_app import celery_app


@celery_app.task(name="integration.retry_processor")
def retry_processor() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntRetryQueue

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntRetryQueue).where(
                    IntRetryQueue.is_deleted.is_(False),
                    IntRetryQueue.status.in_(["pending", "processing"]),
                )
            ).all()
        )
        return {"status": "ok", "retries_due": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.dead_letter_reprocessor")
def dead_letter_reprocessor() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntDeadLetter

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntDeadLetter).where(
                    IntDeadLetter.is_deleted.is_(False),
                    IntDeadLetter.status == "open",
                )
            ).all()
        )
        return {"status": "ok", "dlq_open": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.webhook_dispatcher")
def webhook_dispatcher() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntWebhook

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntWebhook).where(
                    IntWebhook.is_deleted.is_(False),
                    IntWebhook.is_enabled.is_(True),
                    IntWebhook.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "webhooks": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.sync_scheduler")
def sync_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntSyncJob

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntSyncJob).where(
                    IntSyncJob.is_deleted.is_(False),
                    IntSyncJob.status.in_(["approved", "queued"]),
                )
            ).all()
        )
        return {"status": "ok", "syncs_due": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.rate_limit_enforcer")
def rate_limit_enforcer() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntRateLimit

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntRateLimit).where(
                    IntRateLimit.is_deleted.is_(False),
                    IntRateLimit.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "limits": len(rows)}
    finally:
        db.close()


@celery_app.task(name="integration.message_queue_poller")
def message_queue_poller() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.integration.models import IntMessage

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(IntMessage).where(
                    IntMessage.is_deleted.is_(False),
                    IntMessage.status == "queued",
                )
            ).all()
        )
        return {"status": "ok", "queued": len(rows)}
    finally:
        db.close()
