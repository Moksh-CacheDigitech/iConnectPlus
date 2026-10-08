"""Finance port — portal fees through platform IFinancePosting."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.platform.helpers.system_journal import post_two_line_system_journal
from modules.portal.models import PtInvoiceView


class PortalFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def resolve_invoice_ref(self, ctx: TenantContext, finance_invoice_id: UUID | None) -> UUID | None:
        _ = ctx
        return finance_invoice_id

    def post_portal_fee(
        self,
        ctx: TenantContext,
        row: PtInvoiceView,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        resolved_branch_id = getattr(row, "branch_id", None) or ctx.branch_id
        if resolved_branch_id is None:
            raise ValueError("branch_id is required for portal finance posting")
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=row.company_id,
            branch_id=resolved_branch_id,
            description=f"Portal fee {row.view_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=f"portal.fee:{row.id}",
            source_module="portal",
            source_document_type="portal_invoice_view",
            source_document_id=row.id,
            debit_desc="Portal fee debit",
            credit_desc="Portal fee credit",
            fiscal_year_id=fiscal_year_id,
        )
