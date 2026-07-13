"""AR/AP sub-ledger repository."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.finance.models.ledger import FinCustomerLedger, FinVendorLedger
from modules.finance.repository.base import FinanceScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class SubLedgerRepository(FinanceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_customer_ledger(
        self, ctx: TenantContext, company_id: UUID, customer_id: UUID | None = None
    ) -> list[FinCustomerLedger]:
        stmt = select(FinCustomerLedger).where(FinCustomerLedger.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinCustomerLedger, ctx, branch_scoped=True)
        if customer_id:
            stmt = stmt.where(FinCustomerLedger.customer_id == customer_id)
        return list(self.db.scalars(stmt).all())

    def get_customer_entry(self, ctx: TenantContext, entry_id: UUID) -> FinCustomerLedger | None:
        stmt = select(FinCustomerLedger).where(
            FinCustomerLedger.id == entry_id,
            FinCustomerLedger.tenant_id == ctx.tenant_id,
            FinCustomerLedger.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create_customer_entry(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> FinCustomerLedger:
        row = FinCustomerLedger(
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

    def update_customer_entry(
        self, ctx: TenantContext, entry_id: UUID, **fields: object
    ) -> FinCustomerLedger | None:
        row = self.get_customer_entry(ctx, entry_id)
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

    def list_vendor_ledger(
        self, ctx: TenantContext, company_id: UUID, vendor_id: UUID | None = None
    ) -> list[FinVendorLedger]:
        stmt = select(FinVendorLedger).where(FinVendorLedger.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinVendorLedger, ctx, branch_scoped=True)
        if vendor_id:
            stmt = stmt.where(FinVendorLedger.vendor_id == vendor_id)
        return list(self.db.scalars(stmt).all())

    def get_vendor_entry(self, ctx: TenantContext, entry_id: UUID) -> FinVendorLedger | None:
        stmt = select(FinVendorLedger).where(
            FinVendorLedger.id == entry_id,
            FinVendorLedger.tenant_id == ctx.tenant_id,
            FinVendorLedger.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create_vendor_entry(
        self, ctx: TenantContext, *, company_id: UUID, branch_id: UUID, **fields: object
    ) -> FinVendorLedger:
        row = FinVendorLedger(
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

    def update_vendor_entry(
        self, ctx: TenantContext, entry_id: UUID, **fields: object
    ) -> FinVendorLedger | None:
        row = self.get_vendor_entry(ctx, entry_id)
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

    def list_open_ar_for_aging(self, ctx: TenantContext, company_id: UUID) -> list[FinCustomerLedger]:
        stmt = select(FinCustomerLedger).where(
            FinCustomerLedger.company_id == company_id,
            FinCustomerLedger.tenant_id == ctx.tenant_id,
            FinCustomerLedger.status.in_(("open", "partial")),
            FinCustomerLedger.is_deleted.is_(False),
        )
        return list(self.db.scalars(stmt).all())

    def list_open_ap_for_aging(self, ctx: TenantContext, company_id: UUID) -> list[FinVendorLedger]:
        stmt = select(FinVendorLedger).where(
            FinVendorLedger.company_id == company_id,
            FinVendorLedger.tenant_id == ctx.tenant_id,
            FinVendorLedger.status.in_(("open", "partial")),
            FinVendorLedger.is_deleted.is_(False),
        )
        return list(self.db.scalars(stmt).all())

    @staticmethod
    def compute_aging_bucket(due_date: date, as_of: date) -> str:
        days = (as_of - due_date).days
        if days <= 30:
            return "0-30"
        if days <= 60:
            return "31-60"
        if days <= 90:
            return "61-90"
        return "90+"
