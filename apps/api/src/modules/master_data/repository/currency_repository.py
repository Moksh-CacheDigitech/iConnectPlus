"""Currency repository."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.domain.entities import CurrencyEntity
from modules.master_data.models.reference import MasterCurrency
from modules.master_data.repository.base import MasterScopedRepository, utcnow


class CurrencyRepository(MasterScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_currencies(
        self, ctx: TenantContext, *, company_id: UUID | None = None
    ) -> list[CurrencyEntity]:
        stmt = select(MasterCurrency)
        stmt = self.apply_master_filter(stmt, MasterCurrency, ctx)
        if company_id:
            stmt = stmt.where(MasterCurrency.company_id == company_id)
        return [self._to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_by_id(self, ctx: TenantContext, currency_id: UUID) -> CurrencyEntity | None:
        stmt = select(MasterCurrency).where(
            MasterCurrency.id == currency_id,
            MasterCurrency.tenant_id == ctx.tenant_id,
            MasterCurrency.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def get_by_code(
        self, ctx: TenantContext, company_id: UUID, currency_code: str
    ) -> MasterCurrency | None:
        stmt = select(MasterCurrency).where(
            MasterCurrency.tenant_id == ctx.tenant_id,
            MasterCurrency.company_id == company_id,
            MasterCurrency.currency_code == currency_code,
            MasterCurrency.is_deleted.is_(False),
        )
        return self.db.scalar(stmt)

    def get_base_currency(self, ctx: TenantContext, company_id: UUID) -> CurrencyEntity | None:
        stmt = select(MasterCurrency).where(
            MasterCurrency.tenant_id == ctx.tenant_id,
            MasterCurrency.company_id == company_id,
            MasterCurrency.is_base_currency.is_(True),
            MasterCurrency.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        return self._to_entity(row) if row else None

    def create(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        currency_code: str,
        currency_name: str,
        symbol: str | None = None,
        decimal_places: int = 2,
        is_base_currency: bool = False,
        exchange_rate: float | None = None,
        rate_effective_date: date | None = None,
    ) -> CurrencyEntity:
        row = MasterCurrency(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            company_id=company_id,
            currency_code=currency_code,
            currency_name=currency_name,
            symbol=symbol,
            decimal_places=decimal_places,
            is_base_currency=is_base_currency,
            exchange_rate=exchange_rate,
            rate_effective_date=rate_effective_date,
            status="active",
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
        )
        self.db.add(row)
        self.db.flush()
        return self._to_entity(row)

    def update(
        self, ctx: TenantContext, currency_id: UUID, **fields: object
    ) -> CurrencyEntity | None:
        stmt = select(MasterCurrency).where(
            MasterCurrency.id == currency_id,
            MasterCurrency.tenant_id == ctx.tenant_id,
            MasterCurrency.is_deleted.is_(False),
        )
        row = self.db.scalar(stmt)
        if row is None:
            return None
        for key, value in fields.items():
            if hasattr(row, key) and value is not None:
                setattr(row, key, value)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        row.version += 1
        self.db.flush()
        return self._to_entity(row)

    def soft_delete(self, ctx: TenantContext, currency_id: UUID) -> bool:
        stmt = select(MasterCurrency).where(
            MasterCurrency.id == currency_id,
            MasterCurrency.tenant_id == ctx.tenant_id,
        )
        row = self.db.scalar(stmt)
        if row is None or row.is_deleted:
            return False
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        self.db.flush()
        return True

    @staticmethod
    def _to_entity(row: MasterCurrency) -> CurrencyEntity:
        return CurrencyEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            company_id=row.company_id,
            currency_code=row.currency_code,
            currency_name=row.currency_name,
            symbol=row.symbol,
            decimal_places=row.decimal_places,
            is_base_currency=row.is_base_currency,
            exchange_rate=float(row.exchange_rate) if row.exchange_rate is not None else None,
            rate_effective_date=row.rate_effective_date,
            status=row.status,
            version=row.version,
            is_deleted=row.is_deleted,
        )
