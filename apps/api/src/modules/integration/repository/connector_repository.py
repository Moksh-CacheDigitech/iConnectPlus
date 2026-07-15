"""Integration IntConnector repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.integration.models import IntConnector
from modules.integration.repository.base import IntegrationScopedRepository, utcnow


class ConnectorRepository(IntegrationScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> IntConnector | None:
        stmt = select(IntConnector).where(IntConnector.id == row_id, IntConnector.is_deleted.is_(False))
        stmt = self.apply_integration_filter(stmt, IntConnector, ctx, branch_scoped=False)
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select(IntConnector).where(
            IntConnector.company_id == company_id,
            IntConnector.is_deleted.is_(False),
        )
        stmt = self.apply_integration_filter(stmt, IntConnector, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> IntConnector:
        row = IntConnector(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> IntConnector | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
