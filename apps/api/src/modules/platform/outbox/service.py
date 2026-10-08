"""Transactional outbox service (IOutbox)."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.platform.outbox.repository import OutboxRepository


class OutboxService:
    def __init__(self, db: Session) -> None:
        self._repo = OutboxRepository(db)
        self._db = db

    def enqueue(
        self,
        *,
        tenant_id: UUID,
        event_type: str,
        aggregate_type: str,
        aggregate_id: UUID,
        payload: dict,
        idempotency_key: str,
        created_by: UUID | None = None,
    ) -> UUID:
        row = self._repo.enqueue(
            tenant_id=tenant_id,
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload=payload,
            idempotency_key=idempotency_key,
            created_by=created_by,
        )
        return row.id
