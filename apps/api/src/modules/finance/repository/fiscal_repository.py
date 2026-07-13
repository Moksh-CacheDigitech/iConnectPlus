"""Fiscal year and period repository."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.finance.models.fiscal import FinFiscalYear, FinPeriod
from modules.finance.repository.base import FinanceScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class FiscalRepository(FinanceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_fiscal_years(self, ctx: TenantContext, company_id: UUID) -> list[FinFiscalYear]:
        stmt = select(FinFiscalYear).where(FinFiscalYear.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinFiscalYear, ctx)
        return list(self.db.scalars(stmt).all())

    def get_fiscal_year(self, ctx: TenantContext, fiscal_year_id: UUID) -> FinFiscalYear | None:
        stmt = select(FinFiscalYear).where(
            FinFiscalYear.id == fiscal_year_id,
            FinFiscalYear.tenant_id == ctx.tenant_id,
            FinFiscalYear.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def get_open_fiscal_year(self, ctx: TenantContext, company_id: UUID) -> FinFiscalYear | None:
        stmt = select(FinFiscalYear).where(
            FinFiscalYear.company_id == company_id,
            FinFiscalYear.tenant_id == ctx.tenant_id,
            FinFiscalYear.status == "open",
            FinFiscalYear.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create_fiscal_year(
        self, ctx: TenantContext, *, company_id: UUID, **fields: object
    ) -> FinFiscalYear:
        row = FinFiscalYear(
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

    def list_periods(
        self, ctx: TenantContext, *, company_id: UUID, fiscal_year_id: UUID | None = None
    ) -> list[FinPeriod]:
        stmt = select(FinPeriod).where(FinPeriod.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinPeriod, ctx)
        if fiscal_year_id:
            stmt = stmt.where(FinPeriod.fiscal_year_id == fiscal_year_id)
        return list(self.db.scalars(stmt.order_by(FinPeriod.period_number)).all())

    def get_period(self, ctx: TenantContext, period_id: UUID) -> FinPeriod | None:
        stmt = select(FinPeriod).where(
            FinPeriod.id == period_id,
            FinPeriod.tenant_id == ctx.tenant_id,
            FinPeriod.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def get_period_for_update(self, ctx: TenantContext, period_id: UUID) -> FinPeriod | None:
        stmt = (
            select(FinPeriod)
            .where(
                FinPeriod.id == period_id,
                FinPeriod.tenant_id == ctx.tenant_id,
                FinPeriod.is_deleted.is_(False),
            )
            .with_for_update()
        )
        return self.db.scalar(stmt)

    def get_period_for_date(
        self, ctx: TenantContext, company_id: UUID, journal_date: date
    ) -> FinPeriod | None:
        stmt = select(FinPeriod).where(
            FinPeriod.company_id == company_id,
            FinPeriod.tenant_id == ctx.tenant_id,
            FinPeriod.start_date <= journal_date,
            FinPeriod.end_date >= journal_date,
            FinPeriod.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def create_period(self, ctx: TenantContext, *, company_id: UUID, **fields: object) -> FinPeriod:
        row = FinPeriod(
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

    def update_period(self, ctx: TenantContext, period_id: UUID, **fields: object) -> FinPeriod | None:
        row = self.get_period(ctx, period_id)
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
