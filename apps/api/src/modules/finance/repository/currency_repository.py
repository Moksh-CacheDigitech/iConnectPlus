"""Currency rate repository."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.finance.models.currency import FinCurrencyRate
from modules.finance.repository.base import FinanceScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class CurrencyRepository(FinanceScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_rates(self, ctx: TenantContext, company_id: UUID) -> list[FinCurrencyRate]:
        stmt = select(FinCurrencyRate).where(FinCurrencyRate.company_id == company_id)
        stmt = self.apply_finance_filter(stmt, FinCurrencyRate, ctx)
        return list(self.db.scalars(stmt).all())

    def get_rate(self, ctx: TenantContext, rate_id: UUID) -> FinCurrencyRate | None:
        stmt = select(FinCurrencyRate).where(
            FinCurrencyRate.id == rate_id,
            FinCurrencyRate.tenant_id == ctx.tenant_id,
            FinCurrencyRate.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def get_effective_rate(
        self, ctx: TenantContext, company_id: UUID, currency_code: str, on_date: date
    ) -> FinCurrencyRate | None:
        stmt = (
            select(FinCurrencyRate)
            .where(
                FinCurrencyRate.company_id == company_id,
                FinCurrencyRate.tenant_id == ctx.tenant_id,
                FinCurrencyRate.currency_code == currency_code,
                FinCurrencyRate.status == "active",
                FinCurrencyRate.effective_from <= on_date,
                FinCurrencyRate.is_deleted.is_(False),
            )
            .order_by(FinCurrencyRate.effective_from.desc())
        )
        rates = list(self.db.scalars(stmt).all())
        for rate in rates:
            if rate.effective_to is None or rate.effective_to >= on_date:
                return rate
        return None

    def create_rate(self, ctx: TenantContext, *, company_id: UUID, **fields: object) -> FinCurrencyRate:
        row = FinCurrencyRate(
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

    def update_rate(self, ctx: TenantContext, rate_id: UUID, **fields: object) -> FinCurrencyRate | None:
        row = self.get_rate(ctx, rate_id)
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key) and value is not None:
                setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return row
