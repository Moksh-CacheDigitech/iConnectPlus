"""Customer credit repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.sales.models.credit import SalesCustomerCredit
from modules.sales.repository.base import SalesScopedRepository, utcnow


class CreditRepository(SalesScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_credits(self, ctx: TenantContext, company_id: UUID) -> list[SalesCustomerCredit]:
        stmt = select(SalesCustomerCredit).where(SalesCustomerCredit.company_id == company_id)
        stmt = self.apply_sales_filter(stmt, SalesCustomerCredit, ctx, branch_scoped=True)
        return list(self.db.scalars(stmt).all())

    def get_credit(self, ctx: TenantContext, credit_id: UUID) -> SalesCustomerCredit | None:
        stmt = select(SalesCustomerCredit).where(
            SalesCustomerCredit.id == credit_id,
            SalesCustomerCredit.tenant_id == ctx.tenant_id,
            SalesCustomerCredit.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def get_by_customer(
        self,
        ctx: TenantContext,
        company_id: UUID,
        customer_id: UUID,
        *,
        branch_id: UUID | None = None,
    ) -> SalesCustomerCredit | None:
        stmt = select(SalesCustomerCredit).where(
            SalesCustomerCredit.company_id == company_id,
            SalesCustomerCredit.customer_id == customer_id,
            SalesCustomerCredit.tenant_id == ctx.tenant_id,
            SalesCustomerCredit.is_deleted.is_(False),
        )
        if branch_id is not None:
            stmt = stmt.where(SalesCustomerCredit.branch_id == branch_id)
        else:
            stmt = stmt.where(SalesCustomerCredit.branch_id.is_(None))
        return self.db.scalar(stmt)

    def create_credit(
        self, ctx: TenantContext, *, company_id: UUID, **fields: object
    ) -> SalesCustomerCredit:
        row = SalesCustomerCredit(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update_credit(
        self, ctx: TenantContext, credit_id: UUID, **fields: object
    ) -> SalesCustomerCredit | None:
        row = self.get_credit(ctx, credit_id)
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

    def soft_delete_credit(self, ctx: TenantContext, credit_id: UUID) -> bool:
        row = self.get_credit(ctx, credit_id)
        if row is None:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True
