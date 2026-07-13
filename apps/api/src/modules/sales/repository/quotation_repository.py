"""Quotation repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.sales.models.quotation import SalesQuotationHeader, SalesQuotationLine
from modules.sales.repository.base import SalesScopedRepository, utcnow


class QuotationRepository(SalesScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_quotations(
        self, ctx: TenantContext, company_id: UUID
    ) -> list[SalesQuotationHeader]:
        stmt = select(SalesQuotationHeader).where(SalesQuotationHeader.company_id == company_id)
        stmt = self.apply_sales_filter(stmt, SalesQuotationHeader, ctx, branch_scoped=True)
        return list(
            self.db.scalars(stmt.order_by(SalesQuotationHeader.document_date.desc())).all()
        )

    def get_quotation(
        self, ctx: TenantContext, quotation_id: UUID
    ) -> SalesQuotationHeader | None:
        stmt = (
            select(SalesQuotationHeader)
            .options(selectinload(SalesQuotationHeader.lines))
            .where(
                SalesQuotationHeader.id == quotation_id,
                SalesQuotationHeader.tenant_id == ctx.tenant_id,
                SalesQuotationHeader.is_deleted.is_(False),
            )
        )
        return self.db.scalar(stmt)

    def get_quotation_for_update(
        self, ctx: TenantContext, quotation_id: UUID
    ) -> SalesQuotationHeader | None:
        stmt = (
            select(SalesQuotationHeader)
            .options(selectinload(SalesQuotationHeader.lines))
            .where(
                SalesQuotationHeader.id == quotation_id,
                SalesQuotationHeader.tenant_id == ctx.tenant_id,
                SalesQuotationHeader.is_deleted.is_(False),
            )
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def create_quotation(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> SalesQuotationHeader:
        row = SalesQuotationHeader(
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

    def update_quotation(
        self, ctx: TenantContext, quotation_id: UUID, **fields: object
    ) -> SalesQuotationHeader | None:
        row = self.get_quotation_for_update(ctx, quotation_id)
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

    def soft_delete_quotation(self, ctx: TenantContext, quotation_id: UUID) -> bool:
        row = self.get_quotation(ctx, quotation_id)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True

    def add_line(
        self, ctx: TenantContext, quotation: SalesQuotationHeader, **fields: object
    ) -> SalesQuotationLine:
        row = SalesQuotationLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=quotation.company_id,
            branch_id=quotation.branch_id,
            quotation_header_id=quotation.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_line(self, ctx: TenantContext, line_id: UUID) -> SalesQuotationLine | None:
        stmt = select(SalesQuotationLine).where(
            SalesQuotationLine.id == line_id,
            SalesQuotationLine.tenant_id == ctx.tenant_id,
            SalesQuotationLine.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def update_line(
        self, ctx: TenantContext, line_id: UUID, **fields: object
    ) -> SalesQuotationLine | None:
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
