"""CRM customer GST registrations and customer expense ledger repositories."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.crm.models import CrmCompanyGst, CrmCustomerExpense
from modules.crm.repository.base import CrmScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class _AccountChildRepository(CrmScopedRepository):
    """Rows owned by a sales account the caller has already been authorised for."""

    model: type

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID):
        stmt = select(self.model).where(self.model.id == row_id)
        return self.db.scalar(self.apply_tenant_filter(stmt, self.model, ctx))

    def list_for_account(self, ctx: TenantContext, company_account_id: UUID) -> list:
        stmt = select(self.model).where(self.model.company_account_id == company_account_id)
        stmt = self.apply_tenant_filter(stmt, self.model, ctx)
        return list(self.db.scalars(stmt.order_by(self.model.created_at.desc())).all())

    def create(self, ctx: TenantContext, **fields):
        row = self.model(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row, **fields):
        for key, value in fields.items():
            setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version = int(row.version or 1) + 1
        self.db.flush()
        return row

    def soft_delete(self, ctx: TenantContext, row) -> None:
        now = utcnow()
        row.is_deleted = True
        row.deleted_at = now
        row.deleted_by = ctx.user_id
        row.updated_at = now
        row.updated_by = ctx.user_id
        self.db.flush()


class CompanyGstRepository(_AccountChildRepository):
    model = CrmCompanyGst

    def find(self, ctx: TenantContext, company_account_id: UUID, gstin: str) -> CrmCompanyGst | None:
        stmt = select(CrmCompanyGst).where(
            CrmCompanyGst.company_account_id == company_account_id,
            CrmCompanyGst.gstin == gstin,
        )
        return self.db.scalar(self.apply_tenant_filter(stmt, CrmCompanyGst, ctx))


class CustomerExpenseRepository(_AccountChildRepository):
    model = CrmCustomerExpense

    def list_for_opportunity(self, ctx: TenantContext, opportunity_id: UUID) -> list[CrmCustomerExpense]:
        stmt = select(CrmCustomerExpense).where(CrmCustomerExpense.opportunity_id == opportunity_id)
        stmt = self.apply_tenant_filter(stmt, CrmCustomerExpense, ctx)
        return list(self.db.scalars(stmt.order_by(CrmCustomerExpense.expense_date.desc())).all())
