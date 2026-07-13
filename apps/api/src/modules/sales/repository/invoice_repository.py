"""Invoice repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from modules.foundation.domain.value_objects import TenantContext
from modules.sales.models.invoice import SalesInvoiceHeader, SalesInvoiceLine
from modules.sales.repository.base import SalesScopedRepository, utcnow


class InvoiceRepository(SalesScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_invoices(
        self, ctx: TenantContext, company_id: UUID
    ) -> list[SalesInvoiceHeader]:
        stmt = select(SalesInvoiceHeader).where(SalesInvoiceHeader.company_id == company_id)
        stmt = self.apply_sales_filter(stmt, SalesInvoiceHeader, ctx, branch_scoped=True)
        return list(
            self.db.scalars(stmt.order_by(SalesInvoiceHeader.document_date.desc())).all()
        )

    def get_invoice(
        self, ctx: TenantContext, invoice_id: UUID
    ) -> SalesInvoiceHeader | None:
        stmt = (
            select(SalesInvoiceHeader)
            .options(selectinload(SalesInvoiceHeader.lines))
            .where(
                SalesInvoiceHeader.id == invoice_id,
                SalesInvoiceHeader.tenant_id == ctx.tenant_id,
                SalesInvoiceHeader.is_deleted.is_(False),
            )
        )
        return self.db.scalar(stmt)

    def get_invoice_for_update(
        self, ctx: TenantContext, invoice_id: UUID
    ) -> SalesInvoiceHeader | None:
        stmt = (
            select(SalesInvoiceHeader)
            .options(selectinload(SalesInvoiceHeader.lines))
            .where(
                SalesInvoiceHeader.id == invoice_id,
                SalesInvoiceHeader.tenant_id == ctx.tenant_id,
                SalesInvoiceHeader.is_deleted.is_(False),
            )
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def create_invoice(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> SalesInvoiceHeader:
        row = SalesInvoiceHeader(
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

    def update_invoice(
        self, ctx: TenantContext, invoice_id: UUID, **fields: object
    ) -> SalesInvoiceHeader | None:
        row = self.get_invoice_for_update(ctx, invoice_id)
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

    def soft_delete_invoice(self, ctx: TenantContext, invoice_id: UUID) -> bool:
        row = self.get_invoice(ctx, invoice_id)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True

    def add_line(
        self, ctx: TenantContext, invoice: SalesInvoiceHeader, **fields: object
    ) -> SalesInvoiceLine:
        row = SalesInvoiceLine(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=invoice.company_id,
            branch_id=invoice.branch_id,
            invoice_header_id=invoice.id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_line(self, ctx: TenantContext, line_id: UUID) -> SalesInvoiceLine | None:
        stmt = select(SalesInvoiceLine).where(
            SalesInvoiceLine.id == line_id,
            SalesInvoiceLine.tenant_id == ctx.tenant_id,
            SalesInvoiceLine.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def update_line(
        self, ctx: TenantContext, line_id: UUID, **fields: object
    ) -> SalesInvoiceLine | None:
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
