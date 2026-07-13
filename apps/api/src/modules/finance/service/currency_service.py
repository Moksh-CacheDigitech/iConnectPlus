"""Currency rate service."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.finance.repository.currency_repository import CurrencyRepository
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class CurrencyService:
    def __init__(self, db: Session) -> None:
        self._repo = CurrencyRepository(db)
        self._scope = FinanceScopeValidator(db)
        self._audit = AuditService(db)

    def list_rates(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rates(ctx, cid)

    def create_rate(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        rate = self._repo.create_rate(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_currency_rate",
            entity_id=rate.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return rate

    def resolve_rate(
        self, ctx: TenantContext, company_id: UUID, currency_code: str, on_date: date
    ):
        rate = self._repo.get_effective_rate(ctx, company_id, currency_code, on_date)
        if rate is None:
            raise NotFoundException(f"No exchange rate for {currency_code} on {on_date}")
        return rate
