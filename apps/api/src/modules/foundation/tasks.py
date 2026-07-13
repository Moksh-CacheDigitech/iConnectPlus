"""Celery tasks for foundation module."""

from uuid import UUID

from database.session import SessionLocal
from modules.foundation.models.notification import NtfDelivery, NtfEvent
from modules.foundation.repository.base import utcnow
from workers.celery_app import celery_app


@celery_app.task(name="foundation.send_notification")
def send_notification_task(event_id: str, delivery_id: str) -> dict:
    db = SessionLocal()
    try:
        event = db.get(NtfEvent, UUID(event_id))
        delivery = db.get(NtfDelivery, UUID(delivery_id))
        if event is None or delivery is None:
            return {"status": "not_found"}
        delivery.status = "delivered"
        delivery.delivered_at = utcnow()
        event.status = "sent"
        db.commit()
        return {"status": "delivered", "event_id": event_id}
    finally:
        db.close()


@celery_app.task(name="foundation.workflow_escalation")
def workflow_escalation_stub() -> dict:
    """Stub for SLA-based workflow escalation — full logic in Sprint 2+."""
    return {"status": "stub", "escalated": 0}
