"""Sales order repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.sales.models.order import SalesOrderHeader, SalesOrderLine
from modules.sales.repository.base import SalesScopedRepository, utcnow


class OrderRepository(SalesScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_orders(self, ctx: TenantContext, company_id: UUID) -> list[SalesOrderHeader]:
        stmt = select(SalesOrderHeader).where(SalesOrderHeader.company_id == company_id)
        stmt = self.apply_sales_filter(stmt, SalesOrderHeader, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt.order_by(SalesOrderHeader.document_date.desc())).all())

    def get_order(self, ctx: TenantContext, order_id: UUID) -> SalesOrderHeader | None:
        stmt = (
            select(SalesOrderHeader)
            .options(selectinload(SalesOrderHeader.lines))
            .where(
                SalesOrderHeader.id == order_id,
                SalesOrderHeader.tenant_id == ctx.tenant_id,
                SalesOrderHeader.is_deleted.is_(False),
            )
        )
        return self.db.scalar(stmt)

    def get_order_for_update(
        self, ctx: TenantContext, order_id: UUID
    ) -> SalesOrderHeader | None:
        stmt = (
            select(SalesOrderHeader)
            .options(selectinload(SalesOrderHeader.lines))
            .where(
                SalesOrderHeader.id == order_id,
                SalesOrderHeader.tenant_id == ctx.tenant_id,
                SalesOrderHeader.is_deleted.is_(False),
            )
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def create_order(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> SalesOrderHeader:
        row = SalesOrderHeader(
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

    def update_order(
        self, ctx: TenantContext, order_id: UUID, **fields: object
    ) -> SalesOrderHeader | None:
        row = self.get_order_for_update(ctx, order_id)
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

    def soft_delete_order(self, ctx: TenantContext, order_id: UUID) -> bool:
        row = self.get_order(ctx, order_id)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True

    def add_line(
        self, ctx: TenantContext, order: SalesOrderHeader, **fields: object
    ) -> SalesOrderLine:
        row = SalesOrderLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=order.company_id,
            branch_id=order.branch_id,
            order_header_id=order.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_line(self, ctx: TenantContext, line_id: UUID) -> SalesOrderLine | None:
        stmt = select(SalesOrderLine).where(
            SalesOrderLine.id == line_id,
            SalesOrderLine.tenant_id == ctx.tenant_id,
            SalesOrderLine.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def update_line(
        self, ctx: TenantContext, line_id: UUID, **fields: object
    ) -> SalesOrderLine | None:
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
