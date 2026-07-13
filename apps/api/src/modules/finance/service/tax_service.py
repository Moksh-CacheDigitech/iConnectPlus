"""Tax register service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.repository.tax_repository import TaxRepository
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext


class TaxService:
    def __init__(self, db: Session) -> None:
        self._repo = TaxRepository(db)
        self._scope = FinanceScopeValidator(db)

    def list_register(self, ctx: TenantContext, company_id: UUID | None = None, period_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_register(ctx, cid, period_id)

    def period_summary(self, ctx: TenantContext, period_id: UUID, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.period_summary(ctx, cid, period_id)
