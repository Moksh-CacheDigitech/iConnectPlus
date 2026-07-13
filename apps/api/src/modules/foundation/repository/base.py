"""Shared repository utilities."""

import hashlib
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TenantScopedRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def ensure_tenant(tenant_id: UUID, entity_tenant_id: UUID) -> None:
        if tenant_id != entity_tenant_id:
            from core.exceptions import ForbiddenException

            raise ForbiddenException("Cross-tenant access denied")
