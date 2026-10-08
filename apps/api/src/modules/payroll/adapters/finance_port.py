"""Finance port — payroll posts through platform IFinancePosting."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.models import PayPayrollPosting
from modules.platform.helpers.system_journal import post_two_line_system_journal


class PayrollFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def post_salary_expense(
        self,
        ctx: TenantContext,
        posting: PayPayrollPosting,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=posting.company_id,
            branch_id=posting.branch_id,
            description=f"Payroll posting {posting.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=f"payroll.posting:{posting.id}",
            source_module="payroll",
            source_document_type="payroll_posting",
            source_document_id=posting.id,
            debit_desc="Salary expense",
            credit_desc="Payroll liability",
            journal_date=posting.created_at.date() if posting.created_at else None,
            fiscal_year_id=fiscal_year_id,
        )
