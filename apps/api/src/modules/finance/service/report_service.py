"""Finance reporting service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.service.customer_ledger_service import CustomerLedgerService
from modules.finance.service.engines.balance_engine import BalanceEngine
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.finance.service.vendor_ledger_service import VendorLedgerService
from modules.foundation.domain.value_objects import TenantContext


class ReportService:
    def __init__(self, db: Session) -> None:
        self._balance = BalanceEngine(db)
        self._scope = FinanceScopeValidator(db)
        self._ar = CustomerLedgerService(db)
        self._ap = VendorLedgerService(db)

    def trial_balance(self, ctx: TenantContext, period_id: UUID, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._balance.trial_balance(ctx, cid, period_id)

    def ar_aging(self, ctx: TenantContext, company_id: UUID | None = None):
        return self._ar.aging_report(ctx, company_id)

    def ap_aging(self, ctx: TenantContext, company_id: UUID | None = None):
        return self._ap.aging_report(ctx, company_id)
