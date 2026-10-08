"""Transactional outbox port."""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID


class IOutbox(Protocol):
    def enqueue(
        self,
        *,
        tenant_id: UUID,
        event_type: str,
        aggregate_type: str,
        aggregate_id: UUID,
        payload: dict[str, Any],
        idempotency_key: str,
        created_by: UUID | None = None,
    ) -> UUID:
        """Persist outbox row in the current DB transaction. Returns message id."""
        ...
