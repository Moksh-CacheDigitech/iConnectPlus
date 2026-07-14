"""Manufacturing production order repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.models import MfgProductionOperation, MfgProductionOrder
from modules.manufacturing.repository.base import MfgScopedRepository, utcnow


class ProductionOrderRepository(MfgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, order_id: UUID) -> MfgProductionOrder | None:
        stmt = (
            select(MfgProductionOrder)
            .options(selectinload(MfgProductionOrder.operations))
            .where(MfgProductionOrder.id == order_id, MfgProductionOrder.is_deleted.is_(False))
        )
        stmt = self.apply_mfg_filter(stmt, MfgProductionOrder, ctx, branch_scoped=True)
        return self.db.scalar(stmt)

    def list_orders(self, ctx: TenantContext, company_id: UUID):
        stmt = (
            select(MfgProductionOrder)
            .options(selectinload(MfgProductionOrder.operations))
            .where(
                MfgProductionOrder.company_id == company_id,
                MfgProductionOrder.is_deleted.is_(False),
            )
        )
        stmt = self.apply_mfg_filter(stmt, MfgProductionOrder, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> MfgProductionOrder:
        row = MfgProductionOrder(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def add_operation(
        self, ctx: TenantContext, order: MfgProductionOrder, **fields
    ) -> MfgProductionOperation:
        op = MfgProductionOperation(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=order.company_id,
            branch_id=order.branch_id,
            production_order_id=order.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(op)
        self.db.flush()
        return op

    def update(self, ctx: TenantContext, order_id: UUID, **fields) -> MfgProductionOrder | None:
        row = self.get(ctx, order_id)
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
