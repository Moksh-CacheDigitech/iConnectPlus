"""INotify → Foundation NotificationService."""

from __future__ import annotations

from sqlalchemy.orm import Session

from modules.foundation.service.notification_service import NotificationService
from modules.platform.dto import NotifyIntent


class NotifyAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._ntf = NotificationService(db)

    def publish(self, intent: NotifyIntent):
        if intent.idempotency_key:
            # Deduplicate via platform idempotency table when key provided.
            from sqlalchemy import select

            from modules.platform.models.idempotency import FndIdempotencyRecord

            stmt = select(FndIdempotencyRecord).where(
                FndIdempotencyRecord.tenant_id == intent.tenant_id,
                FndIdempotencyRecord.scope == "notify.publish",
                FndIdempotencyRecord.idempotency_key == intent.idempotency_key,
            )
            existing = self._db.scalars(stmt).first()
            if existing is not None:
                return existing.result_json

        template = self._ntf.get_or_create_template(
            tenant_id=intent.tenant_id,
            template_code=intent.template_code,
            template_name=intent.template_code.replace(".", " ").title(),
            channel=intent.channel,
            body_template="{{body}}",
            subject_template="{{title}}",
            created_by=intent.created_by,
        )
        event = self._ntf.send(
            tenant_id=intent.tenant_id,
            template_id=template.id,
            event_type=intent.event_type,
            recipient_user_id=intent.recipient_user_id,
            recipient_address=intent.recipient_address,
            payload_json=intent.payload,
            created_by=intent.created_by,
            channel_override=intent.channel,
        )
        if intent.idempotency_key:
            from modules.platform.models.idempotency import FndIdempotencyRecord

            self._db.add(
                FndIdempotencyRecord(
                    tenant_id=intent.tenant_id,
                    scope="notify.publish",
                    idempotency_key=intent.idempotency_key,
                    result_json={"event_id": str(getattr(event, "id", event))},
                )
            )
            self._db.flush()
        return event
