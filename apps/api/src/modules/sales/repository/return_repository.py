"""Sales return repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.sales.models.return_doc import SalesReturnHeader, SalesReturnLine
from modules.sales.repository.base import SalesScopedRepository, utcnow


class ReturnRepository(SalesScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_returns(self, ctx: TenantContext, company_id: UUID) -> list[SalesReturnHeader]:
        stmt = select(SalesReturnHeader).where(SalesReturnHeader.company_id == company_id)
        stmt = self.apply_sales_filter(stmt, SalesReturnHeader, ctx, branch_scoped=True)
        return list(
            self.db.scalars(stmt.order_by(SalesReturnHeader.document_date.desc())).all()
        )

    def get_return(self, ctx: TenantContext, return_id: UUID) -> SalesReturnHeader | None:
        stmt = (
            select(SalesReturnHeader)
            .options(selectinload(SalesReturnHeader.lines))
            .where(
                SalesReturnHeader.id == return_id,
                SalesReturnHeader.tenant_id == ctx.tenant_id,
                SalesReturnHeader.is_deleted.is_(False),
            )
        )
        return self.db.scalar(stmt)

    def get_return_for_update(
        self, ctx: TenantContext, return_id: UUID
    ) -> SalesReturnHeader | None:
        stmt = (
            select(SalesReturnHeader)
            .options(selectinload(SalesReturnHeader.lines))
            .where(
                SalesReturnHeader.id == return_id,
                SalesReturnHeader.tenant_id == ctx.tenant_id,
                SalesReturnHeader.is_deleted.is_(False),
            )
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def create_return(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> SalesReturnHeader:
        row = SalesReturnHeader(
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

    def update_return(
        self, ctx: TenantContext, return_id: UUID, **fields: object
    ) -> SalesReturnHeader | None:
        row = self.get_return_for_update(ctx, return_id)
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

    def soft_delete_return(self, ctx: TenantContext, return_id: UUID) -> bool:
        row = self.get_return(ctx, return_id)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True

    def add_line(
        self, ctx: TenantContext, return_header: SalesReturnHeader, **fields: object
    ) -> SalesReturnLine:
        row = SalesReturnLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=return_header.company_id,
            branch_id=return_header.branch_id,
            return_header_id=return_header.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_line(self, ctx: TenantContext, line_id: UUID) -> SalesReturnLine | None:
        stmt = select(SalesReturnLine).where(
            SalesReturnLine.id == line_id,
            SalesReturnLine.tenant_id == ctx.tenant_id,
            SalesReturnLine.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def update_line(
        self, ctx: TenantContext, line_id: UUID, **fields: object
    ) -> SalesReturnLine | None:
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
