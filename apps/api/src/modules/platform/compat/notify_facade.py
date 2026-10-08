"""NotificationService-compatible facade over INotify / outbox."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from modules.platform.adapters.notify_adapter import NotifyAdapter
from modules.platform.dto import NotifyIntent
from modules.platform.helpers.side_effects import enqueue_notify


class PlatformNotifyFacade:
    """Prefer outbox enqueue; sync publish available for immediate delivery."""

    def __init__(self, db: Session, *, use_outbox: bool = True) -> None:
        self._db = db
        self._notify = NotifyAdapter(db)
        self._use_outbox = use_outbox

    def send(
        self,
        *,
        tenant_id: UUID,
        template_code: str,
        event_type: str,
        recipient_user_id: UUID | None = None,
        recipient_address: str | None = None,
        payload_json: dict | None = None,
        created_by: UUID | None = None,
        channel: str = "in_app",
        idempotency_key: str | None = None,
        aggregate_id: UUID | None = None,
    ):
        key = idempotency_key or f"notify:{event_type}:{recipient_user_id or recipient_address}:{template_code}"
        if self._use_outbox:
            return enqueue_notify(
                self._db,
                tenant_id=tenant_id,
                template_code=template_code,
                event_type=event_type,
                aggregate_id=aggregate_id or tenant_id,
                recipient_user_id=recipient_user_id,
                recipient_address=recipient_address,
                payload=payload_json or {},
                channel=channel,
                idempotency_key=key,
                created_by=created_by,
            )
        return self._notify.publish(
            NotifyIntent(
                tenant_id=tenant_id,
                event_type=event_type,
                template_code=template_code,
                recipient_user_id=recipient_user_id,
                recipient_address=recipient_address,
                payload=payload_json or {},
                channel=channel,
                idempotency_key=key,
                created_by=created_by,
            )
        )
