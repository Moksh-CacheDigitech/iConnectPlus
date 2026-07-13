"""General ledger read engine."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.entities import AccountStatementLine
from modules.finance.repository.coa_repository import COARepository
from modules.finance.repository.gl_repository import GLRepository
from modules.foundation.domain.value_objects import TenantContext


class LedgerEngine:
    def __init__(self, db: Session) -> None:
        self._gl = GLRepository(db)
        self._coa = COARepository(db)

    def list_entries(
        self,
        ctx: TenantContext,
        company_id: UUID,
        *,
        account_id: UUID | None = None,
        period_id: UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ):
        return self._gl.list_entries(
            ctx,
            company_id,
            account_id=account_id,
            period_id=period_id,
            from_date=from_date,
            to_date=to_date,
        )

    def account_statement(
        self,
        ctx: TenantContext,
        company_id: UUID,
        account_id: UUID,
        *,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[AccountStatementLine]:
        account = self._coa.get_account(ctx, account_id)
        if account is None:
            return []
        entries = self._gl.list_entries(
            ctx, company_id, account_id=account_id, from_date=from_date, to_date=to_date
        )
        running = Decimal("0")
        lines: list[AccountStatementLine] = []
        for entry in entries:
            debit = Decimal(str(entry.base_debit_amount))
            credit = Decimal(str(entry.base_credit_amount))
            running += debit - credit
            lines.append(
                AccountStatementLine(
                    entry_date=entry.entry_date,
                    entry_number=entry.entry_number,
                    description=entry.description,
                    debit_amount=debit,
                    credit_amount=credit,
                    running_balance=running,
                )
            )
        return lines
