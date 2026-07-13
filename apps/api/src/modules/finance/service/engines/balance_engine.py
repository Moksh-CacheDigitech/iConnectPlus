"""Account balance and trial balance engine."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.entities import TrialBalanceLine
from modules.finance.repository.coa_repository import COARepository
from modules.finance.repository.gl_repository import GLRepository
from modules.foundation.domain.value_objects import TenantContext


class BalanceEngine:
    def __init__(self, db: Session) -> None:
        self._gl = GLRepository(db)
        self._coa = COARepository(db)

    def trial_balance(
        self, ctx: TenantContext, company_id: UUID, period_id: UUID
    ) -> list[TrialBalanceLine]:
        rows = self._gl.trial_balance(ctx, company_id, period_id)
        lines: list[TrialBalanceLine] = []
        for account_id, account_code, debit_total, credit_total in rows:
            account = self._coa.get_account(ctx, account_id)
            debit = Decimal(str(debit_total))
            credit = Decimal(str(credit_total))
            lines.append(
                TrialBalanceLine(
                    account_id=account_id,
                    account_code=account_code,
                    account_name=account.account_name if account else account_code,
                    debit_total=debit,
                    credit_total=credit,
                    balance=debit - credit,
                )
            )
        return lines

    def account_balance(
        self, ctx: TenantContext, company_id: UUID, account_id: UUID, period_id: UUID
    ) -> Decimal:
        rows = self._gl.trial_balance(ctx, company_id, period_id)
        for row_account_id, _, debit_total, credit_total in rows:
            if row_account_id == account_id:
                return Decimal(str(debit_total)) - Decimal(str(credit_total))
        return Decimal("0")
