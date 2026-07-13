"""General ledger repository — read and post only."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from modules.finance.models.ledger import FinGlEntry
from modules.finance.repository.base import FinanceScopedRepository
from modules.foundation.domain.value_objects import TenantContext


class GLRepository(FinanceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_entries(
        self,
        ctx: TenantContext,
        company_id: UUID,
        *,
        account_id: UUID | None = None,
        period_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[FinGlEntry]:
        stmt = select(FinGlEntry).where(FinGlEntry.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinGlEntry, ctx, branch_scoped=True)
        if account_id:
            stmt = stmt.where(FinGlEntry.account_id == account_id)
        if period_id:
            stmt = stmt.where(FinGlEntry.period_id == period_id)
        if from_date:
            stmt = stmt.where(FinGlEntry.entry_date >= from_date)
        if to_date:
            stmt = stmt.where(FinGlEntry.entry_date <= to_date)
        return list(self.db.scalars(stmt.order_by(FinGlEntry.entry_date, FinGlEntry.entry_number)).all())

    def exists_for_journal(self, journal_header_id: UUID) -> bool:
        stmt = select(FinGlEntry.id).where(FinGlEntry.journal_header_id == journal_header_id).limit(1)
        return self.db.scalar(stmt) is not None

    def create_entry(self, ctx: TenantContext, **fields: object) -> FinGlEntry:
        row = FinGlEntry(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def trial_balance(
        self,
        ctx: TenantContext,
        company_id: UUID,
        period_id: UUID,
    ) -> list[tuple[UUID, str, float, float]]:
        stmt = (
            select(
                FinGlEntry.account_id,
                FinGlEntry.account_code,
                func.coalesce(func.sum(FinGlEntry.base_debit_amount), 0),
                func.coalesce(func.sum(FinGlEntry.base_credit_amount), 0),
            )
            .where(
                FinGlEntry.company_id == company_id,
                FinGlEntry.tenant_id == ctx.tenant_id,
                FinGlEntry.period_id == period_id,
            )
            .group_by(FinGlEntry.account_id, FinGlEntry.account_code)
        )
        if ctx.branch_id and ctx.user_type not in {"super_admin", "tenant_admin"}:
            stmt = stmt.where(FinGlEntry.branch_id == ctx.branch_id)
        return list(self.db.execute(stmt).all())  # type: ignore[arg-type]
