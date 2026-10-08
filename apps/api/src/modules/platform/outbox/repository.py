"""Outbox persistence."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.platform.models.outbox import FndOutboxMessage


class OutboxRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_idempotency(
        self, tenant_id: UUID, idempotency_key: str
    ) -> FndOutboxMessage | None:
        stmt = select(FndOutboxMessage).where(
            FndOutboxMessage.tenant_id == tenant_id,
            FndOutboxMessage.idempotency_key == idempotency_key,
        )
        return self.db.scalars(stmt).first()

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
    ) -> FndOutboxMessage:
        existing = self.get_by_idempotency(tenant_id, idempotency_key)
        if existing is not None:
            return existing

        row = FndOutboxMessage(
            tenant_id=tenant_id,
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            payload_json=payload,
            idempotency_key=idempotency_key,
            status="pending",
            created_by=created_by,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def claim_batch(self, *, limit: int = 50) -> list[FndOutboxMessage]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(FndOutboxMessage)
            .where(
                FndOutboxMessage.status.in_(("pending", "failed")),
                FndOutboxMessage.available_at <= now,
                FndOutboxMessage.attempts < 10,
            )
            .order_by(FndOutboxMessage.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        rows = list(self.db.scalars(stmt).all())
        for row in rows:
            row.status = "processing"
            row.attempts += 1
        self.db.flush()
        return rows

    def mark_processed(self, row: FndOutboxMessage) -> None:
        row.status = "processed"
        row.processed_at = datetime.now(timezone.utc)
        row.last_error = None
        self.db.flush()

    def mark_failed(self, row: FndOutboxMessage, error: str) -> None:
        row.status = "failed"
        row.last_error = error[:2000]
        # Exponential backoff: 30s * 2^(attempts-1), capped at 1h
        delay = min(3600, 30 * (2 ** max(0, row.attempts - 1)))
        row.available_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
        self.db.flush()
