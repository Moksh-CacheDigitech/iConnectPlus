"""Inventory FIFO valuation layer repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.models.valuation import InvValuationLayer
from modules.inventory.repository.base import InvScopedRepository, utcnow


class ValuationRepository(InvScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_open_fifo(
        self, ctx: TenantContext, *, company_id: UUID, warehouse_id: UUID, product_id: UUID
    ) -> list[InvValuationLayer]:
        stmt = (
            select(InvValuationLayer)
            .where(
                InvValuationLayer.company_id == company_id,
                InvValuationLayer.warehouse_id == warehouse_id,
                InvValuationLayer.product_id == product_id,
                InvValuationLayer.status == "open",
                InvValuationLayer.is_deleted.is_(False),
                InvValuationLayer.remaining_qty > 0,
            )
            .order_by(InvValuationLayer.received_at.asc())
            .with_for_update()
        )
        stmt = self.apply_tenant_filter(stmt, InvValuationLayer, ctx)
        return list(self.db.scalars(stmt).all())

    def list_layers(self, ctx: TenantContext, company_id: UUID, warehouse_id: UUID | None = None):
        stmt = select(InvValuationLayer).where(
            InvValuationLayer.company_id == company_id, InvValuationLayer.is_deleted.is_(False)
        )
        if warehouse_id:
            stmt = stmt.where(InvValuationLayer.warehouse_id == warehouse_id)
        stmt = self.apply_inv_filter(stmt, InvValuationLayer, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> InvValuationLayer:
        row = InvValuationLayer(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields
        )
        self.db.add(row)
        self.db.flush()
        return row

    def touch(self, row: InvValuationLayer, ctx: TenantContext) -> None:
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
