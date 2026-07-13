"""General ledger service."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.service.engines.ledger_engine import LedgerEngine
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext


class GeneralLedgerService:
    def __init__(self, db: Session) -> None:
        self._ledger = LedgerEngine(db)
        self._scope = FinanceScopeValidator(db)

    def list_entries(
        self,
        ctx: TenantContext,
        company_id: UUID | None = None,
        *,
        account_id: UUID | None = None,
        period_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._ledger.list_entries(
            ctx, cid, account_id=account_id, period_id=period_id, from_date=from_date, to_date=to_date
        )

    def account_statement(
        self,
        ctx: TenantContext,
        account_id: UUID,
        company_id: UUID | None = None,
        *,
        from_date: date | None = None,
        to_date: date | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._ledger.account_statement(
            ctx, cid, account_id, from_date=from_date, to_date=to_date
        )
