"""Finance port — service expenses through platform IFinancePosting."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.platform.helpers.system_journal import post_two_line_system_journal
from modules.service.models import SvcServiceExpense


class ServiceFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def post_expense(
        self,
        ctx: TenantContext,
        row: SvcServiceExpense,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            description=f"Service expense {row.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=f"service.expense:{row.id}",
            source_module="service",
            source_document_type="service_expense",
            source_document_id=row.id,
            debit_desc="Service expense debit",
            credit_desc="Service expense credit",
            journal_date=row.incurred_on or date.today(),
            fiscal_year_id=fiscal_year_id,
        )
