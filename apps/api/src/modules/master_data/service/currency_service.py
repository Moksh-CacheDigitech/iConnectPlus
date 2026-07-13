"""Currency service."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.models.reference import MasterCurrency
from modules.master_data.repository.currency_repository import CurrencyRepository
from modules.master_data.service.duplicate_checker_service import DuplicateCheckerService
from modules.master_data.service.master_scope_validator import MasterScopeValidator


class CurrencyService:
    def __init__(self, db: Session) -> None:
        self._repo = CurrencyRepository(db)
        self._audit = AuditService(db)
        self._duplicates = DuplicateCheckerService(db)
        self._scope = MasterScopeValidator(db)

    def list_currencies(self, ctx: TenantContext, *, company_id: UUID | None = None):
        if company_id:
            self._scope.validate_company_access(ctx, company_id)
        return self._repo.list_currencies(ctx, company_id=company_id)

    def get_currency(self, ctx: TenantContext, currency_id: UUID):
        currency = self._repo.get_by_id(ctx, currency_id)
        if currency is None:
            raise NotFoundException("Currency not found")
        self._scope.validate_company_access(ctx, currency.company_id)
        return currency

    def create_currency(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        currency_code: str,
        currency_name: str,
        symbol: str | None = None,
        decimal_places: int = 2,
        is_base_currency: bool = False,
        exchange_rate: float | None = None,
        rate_effective_date: date | None = None,
    ):
        resolved_company_id = self._scope.resolve_company_id(ctx, company_id)
        self._duplicates.ensure_unique_code(
            model=MasterCurrency,
            company_id=resolved_company_id,
            code=currency_code,
            code_field="currency_code",
            label="Currency",
        )
        if is_base_currency and self._repo.get_base_currency(ctx, resolved_company_id) is not None:
            raise ConflictException("A base currency already exists for this company")

        currency = self._repo.create(
            ctx,
            company_id=resolved_company_id,
            currency_code=currency_code,
            currency_name=currency_name,
            symbol=symbol,
            decimal_places=decimal_places,
            is_base_currency=is_base_currency,
            exchange_rate=exchange_rate,
            rate_effective_date=rate_effective_date,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_currency",
            entity_id=currency.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={"currency_code": currency_code, "is_base_currency": is_base_currency},
        )
        return currency

    def update_currency(self, ctx: TenantContext, currency_id: UUID, **fields):
        currency = self.get_currency(ctx, currency_id)
        if fields.get("is_base_currency") and not currency.is_base_currency:
            existing = self._repo.get_base_currency(ctx, currency.company_id)
            if existing is not None and existing.id != currency_id:
                raise ConflictException("A base currency already exists for this company")

        updated = self._repo.update(ctx, currency_id, **fields)
        if updated is None:
            raise NotFoundException("Currency not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_currency",
            entity_id=currency_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def delete_currency(self, ctx: TenantContext, currency_id: UUID) -> None:
        self.get_currency(ctx, currency_id)
        if not self._repo.soft_delete(ctx, currency_id):
            raise NotFoundException("Currency not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_currency",
            entity_id=currency_id,
            operation="delete",
            performed_by=ctx.user_id,
        )
