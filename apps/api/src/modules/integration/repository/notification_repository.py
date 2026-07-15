"""Integration IntNotification repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.integration.models import IntNotification
from modules.integration.repository.base import IntegrationScopedRepository, utcnow


class NotificationRepository(IntegrationScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> IntNotification | None:
        stmt = select(IntNotification).where(IntNotification.id == row_id, IntNotification.is_deleted.is_(False))
        stmt = self.apply_integration_filter(stmt, IntNotification, ctx, branch_scoped=False)
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select(IntNotification).where(
            IntNotification.company_id == company_id,
            IntNotification.is_deleted.is_(False),
        )
        stmt = self.apply_integration_filter(stmt, IntNotification, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> IntNotification:
        row = IntNotification(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> IntNotification | None:
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
