"""Finance port — ecommerce payments through platform IFinancePosting."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.ecommerce.models import EcPayment
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.helpers.system_journal import post_two_line_system_journal


class EcommerceFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def post_payment_capture(
        self,
        ctx: TenantContext,
        row: EcPayment,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_journal(
            ctx,
            row=row,
            document_label=f"Payment {row.payment_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            idempotency_key=f"ecommerce.payment.capture:{row.id}",
        )

    def post_payment_refund(
        self,
        ctx: TenantContext,
        row: EcPayment,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_journal(
            ctx,
            row=row,
            document_label=f"Refund {row.payment_number}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
            idempotency_key=f"ecommerce.payment.refund:{row.id}",
        )

    def _post_journal(
        self,
        ctx: TenantContext,
        *,
        row: EcPayment,
        document_label: str,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None,
        idempotency_key: str,
    ) -> UUID:
        resolved_branch_id = row.branch_id if row.branch_id is not None else ctx.branch_id
        if resolved_branch_id is None:
            raise ValueError("branch_id is required for E-Commerce finance posting")
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=row.company_id,
            branch_id=resolved_branch_id,
            description=f"E-Commerce {document_label}",
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=idempotency_key,
            source_module="ecommerce",
            source_document_type="ecommerce_payment",
            source_document_id=row.id,
            debit_desc="E-Commerce debit",
            credit_desc="E-Commerce credit",
            fiscal_year_id=fiscal_year_id,
        )
