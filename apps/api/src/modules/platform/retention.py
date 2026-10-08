"""Soft-delete + retention helpers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from modules.foundation.repository.base import utcnow


def soft_delete(entity: Any, *, deleted_by: UUID | None) -> None:
    entity.is_deleted = True
    entity.deleted_at = utcnow()
    entity.deleted_by = deleted_by


def restore(entity: Any) -> None:
    entity.is_deleted = False
    entity.deleted_at = None
    entity.deleted_by = None


# Retention windows by table class (ops guidance encoded for jobs).
RETENTION_DAYS: dict[str, int] = {
    "operational": 365 * 3,
    "audit": 365 * 10,
    "notification": 365,
    "outbox_processed": 90,
    "session": 30,
}


def purge_cutoff(table_class: str) -> datetime:
    days = RETENTION_DAYS.get(table_class, RETENTION_DAYS["operational"])
    return datetime.now(timezone.utc) - timedelta(days=days)
