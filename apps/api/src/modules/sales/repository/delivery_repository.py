"""Delivery repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.sales.models.delivery import SalesDeliveryHeader, SalesDeliveryLine
from modules.sales.repository.base import SalesScopedRepository, utcnow


class DeliveryRepository(SalesScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_deliveries(
        self, ctx: TenantContext, company_id: UUID
    ) -> list[SalesDeliveryHeader]:
        stmt = select(SalesDeliveryHeader).where(SalesDeliveryHeader.company_id == company_id)
        stmt = self.apply_sales_filter(stmt, SalesDeliveryHeader, ctx, branch_scoped=True)
        return list(
            self.db.scalars(stmt.order_by(SalesDeliveryHeader.document_date.desc())).all()
        )

    def get_delivery(
        self, ctx: TenantContext, delivery_id: UUID
    ) -> SalesDeliveryHeader | None:
        stmt = (
            select(SalesDeliveryHeader)
            .options(selectinload(SalesDeliveryHeader.lines))
            .where(
                SalesDeliveryHeader.id == delivery_id,
                SalesDeliveryHeader.tenant_id == ctx.tenant_id,
                SalesDeliveryHeader.is_deleted.is_(False),
            )
        )
        return self.db.scalar(stmt)

    def get_delivery_for_update(
        self, ctx: TenantContext, delivery_id: UUID
    ) -> SalesDeliveryHeader | None:
        stmt = (
            select(SalesDeliveryHeader)
            .options(selectinload(SalesDeliveryHeader.lines))
            .where(
                SalesDeliveryHeader.id == delivery_id,
                SalesDeliveryHeader.tenant_id == ctx.tenant_id,
                SalesDeliveryHeader.is_deleted.is_(False),
            )
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def create_delivery(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> SalesDeliveryHeader:
        row = SalesDeliveryHeader(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            branch_id=branch_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update_delivery(
        self, ctx: TenantContext, delivery_id: UUID, **fields: object
    ) -> SalesDeliveryHeader | None:
        row = self.get_delivery_for_update(ctx, delivery_id)
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key):
                setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return row

    def soft_delete_delivery(self, ctx: TenantContext, delivery_id: UUID) -> bool:
        row = self.get_delivery(ctx, delivery_id)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True

    def add_line(
        self, ctx: TenantContext, delivery: SalesDeliveryHeader, **fields: object
    ) -> SalesDeliveryLine:
        row = SalesDeliveryLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=delivery.company_id,
            branch_id=delivery.branch_id,
            delivery_header_id=delivery.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_line(self, ctx: TenantContext, line_id: UUID) -> SalesDeliveryLine | None:
        stmt = select(SalesDeliveryLine).where(
            SalesDeliveryLine.id == line_id,
            SalesDeliveryLine.tenant_id == ctx.tenant_id,
            SalesDeliveryLine.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def update_line(
        self, ctx: TenantContext, line_id: UUID, **fields: object
    ) -> SalesDeliveryLine | None:
        row = self.get_line(ctx, line_id)
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key):
                setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return row

    def soft_delete_line(self, ctx: TenantContext, line_id: UUID) -> bool:
        row = self.get_line(ctx, line_id)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True
