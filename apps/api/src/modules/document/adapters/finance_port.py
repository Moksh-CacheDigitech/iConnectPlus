"""Finance port — document charges through platform IFinancePosting."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.document.models import DocDocument
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.helpers.system_journal import post_two_line_system_journal


class DocumentFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def post_document_charge(
        self,
        ctx: TenantContext,
        row: DocDocument,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        resolved_branch_id = row.branch_id if row.branch_id is not None else ctx.branch_id
        if resolved_branch_id is None:
            raise ValueError("branch_id is required for document finance posting")
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=row.company_id,
            branch_id=resolved_branch_id,
            description=f"Document charge {row.document_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=f"document.charge:{row.id}",
            source_module="document",
            source_document_type="document",
            source_document_id=row.id,
            debit_desc="Document charge debit",
            credit_desc="Document charge credit",
            fiscal_year_id=fiscal_year_id,
        )
