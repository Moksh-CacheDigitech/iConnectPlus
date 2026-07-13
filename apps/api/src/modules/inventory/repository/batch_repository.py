"""Inventory batch repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.models.batch import InvBatch
from modules.inventory.repository.base import InvScopedRepository, utcnow


class BatchRepository(InvScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, batch_id: UUID) -> InvBatch | None:
        stmt = select(InvBatch).where(InvBatch.id == batch_id, InvBatch.is_deleted.is_(False))
        stmt = self.apply_inv_filter(stmt, InvBatch, ctx)
        return self.db.scalar(stmt)

    def list_batches(self, ctx: TenantContext, company_id: UUID, product_id: UUID | None = None):
        stmt = select(InvBatch).where(
            InvBatch.company_id == company_id, InvBatch.is_deleted.is_(False)
        )
        if product_id:
            stmt = stmt.where(InvBatch.product_id == product_id)
        stmt = self.apply_inv_filter(stmt, InvBatch, ctx)
        return list(self.db.scalars(stmt).all())

    def list_expiring(self, ctx: TenantContext, *, before_date, company_id: UUID | None = None):
        stmt = select(InvBatch).where(
            InvBatch.is_deleted.is_(False),
            InvBatch.status == "active",
            InvBatch.expiry_date.is_not(None),
            InvBatch.expiry_date <= before_date,
        )
        if company_id:
            stmt = stmt.where(InvBatch.company_id == company_id)
        stmt = self.apply_tenant_filter(stmt, InvBatch, ctx)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> InvBatch:
        row = InvBatch(
            id=uuid4(), tenant_id=ctx.tenant_id,
            created_by=ctx.user_id, updated_by=ctx.user_id, **fields
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, batch_id: UUID, **fields) -> InvBatch | None:
        row = self.get(ctx, batch_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
