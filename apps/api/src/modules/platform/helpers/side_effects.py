"""Enqueue notify / audit / domain events in the same DB transaction."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.platform.events import is_registered_domain_event
from modules.platform.outbox.service import OutboxService


def enqueue_audit(
    db: Session,
    *,
    tenant_id: UUID,
    entity_name: str,
    entity_id: UUID,
    operation: str,
    performed_by: UUID | None,
    new_value: dict[str, Any] | None = None,
    old_value: dict[str, Any] | None = None,
    idempotency_key: str,
) -> UUID:
    return OutboxService(db).enqueue(
        tenant_id=tenant_id,
        event_type="audit.entity_change",
        aggregate_type=entity_name,
        aggregate_id=entity_id,
        payload={
            "entity_name": entity_name,
            "entity_id": str(entity_id),
            "operation": operation,
            "performed_by": str(performed_by) if performed_by else None,
            "new_value": new_value,
            "old_value": old_value,
        },
        idempotency_key=idempotency_key,
        created_by=performed_by,
    )


def enqueue_notify(
    db: Session,
    *,
    tenant_id: UUID,
    template_code: str,
    event_type: str,
    aggregate_id: UUID,
    recipient_user_id: UUID | None = None,
    recipient_address: str | None = None,
    payload: dict[str, Any] | None = None,
    channel: str = "in_app",
    idempotency_key: str,
    created_by: UUID | None = None,
) -> UUID:
    return OutboxService(db).enqueue(
        tenant_id=tenant_id,
        event_type="notify.dispatch",
        aggregate_type="notification",
        aggregate_id=aggregate_id,
        payload={
            "template_code": template_code,
            "event_type": event_type,
            "recipient_user_id": str(recipient_user_id) if recipient_user_id else None,
            "recipient_address": recipient_address,
            "payload": payload or {},
            "channel": channel,
            "idempotency_key": idempotency_key,
            "created_by": str(created_by) if created_by else None,
        },
        idempotency_key=idempotency_key,
        created_by=created_by,
    )


def enqueue_domain_event(
    db: Session,
    *,
    tenant_id: UUID,
    event_type: str,
    aggregate_type: str,
    aggregate_id: UUID,
    payload: dict[str, Any],
    idempotency_key: str,
    created_by: UUID | None = None,
) -> UUID:
    if not is_registered_domain_event(event_type):
        raise ValueError(f"Unregistered domain event: {event_type}")
    return OutboxService(db).enqueue(
        tenant_id=tenant_id,
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload,
        idempotency_key=idempotency_key,
        created_by=created_by,
    )
