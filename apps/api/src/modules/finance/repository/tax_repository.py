"""Tax register repository."""

from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.finance.models.tax import FinTaxRegister
from modules.finance.repository.base import FinanceScopedRepository
from modules.foundation.domain.value_objects import TenantContext


class TaxRepository(FinanceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_register(
        self, ctx: TenantContext, company_id: UUID, period_id: UUID | None = None
    ) -> list[FinTaxRegister]:
        stmt = select(FinTaxRegister).where(FinTaxRegister.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinTaxRegister, ctx, branch_scoped=True)
        if period_id:
            stmt = stmt.where(FinTaxRegister.period_id == period_id)
        return list(self.db.scalars(stmt).all())

    def create_register(self, ctx: TenantContext, **fields: object) -> FinTaxRegister:
        row = FinTaxRegister(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def period_summary(
        self, ctx: TenantContext, company_id: UUID, period_id: UUID
    ) -> list[tuple[str, float]]:
        stmt = (
            select(
                FinTaxRegister.transaction_type,
                func.coalesce(func.sum(FinTaxRegister.tax_amount), 0),
            )
            .where(
                FinTaxRegister.company_id == company_id,
                FinTaxRegister.tenant_id == ctx.tenant_id,
                FinTaxRegister.period_id == period_id,
                FinTaxRegister.status == "active",
            )
            .group_by(FinTaxRegister.transaction_type)
        )
        return list(self.db.execute(stmt).all())  # type: ignore[arg-type]
