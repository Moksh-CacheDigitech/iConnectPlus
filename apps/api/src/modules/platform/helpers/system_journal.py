"""Shared two-line system journal posting via IFinancePosting."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.platform.adapters.finance_adapter import FinancePostingAdapter
from modules.platform.dto import JournalLineDraft, SystemJournalDraft
from modules.platform.outbox.service import OutboxService


def post_two_line_system_journal(
    db: Session,
    ctx: TenantContext,
    *,
    company_id: UUID,
    branch_id: UUID,
    description: str,
    amount: Decimal,
    debit_account_id: UUID,
    credit_account_id: UUID,
    idempotency_key: str,
    source_module: str,
    source_document_type: str,
    source_document_id: UUID,
    debit_desc: str = "Debit",
    credit_desc: str = "Credit",
    journal_date: date | None = None,
    fiscal_year_id: UUID | None = None,
    enqueue_audit: bool = True,
) -> UUID:
    """Post a balanced two-line system journal and optionally enqueue an audit outbox event."""
    amount = amount.quantize(Decimal("0.0001"))
    result = FinancePostingAdapter(db).post_system_journal(
        ctx,
        SystemJournalDraft(
            company_id=company_id,
            branch_id=branch_id,
            description=description,
            lines=(
                JournalLineDraft(
                    account_id=debit_account_id,
                    debit_amount=amount,
                    credit_amount=Decimal("0"),
                    description=debit_desc,
                    line_number=1,
                ),
                JournalLineDraft(
                    account_id=credit_account_id,
                    debit_amount=Decimal("0"),
                    credit_amount=amount,
                    description=credit_desc,
                    line_number=2,
                ),
            ),
            idempotency_key=idempotency_key,
            journal_date=journal_date or date.today(),
            fiscal_year_id=fiscal_year_id,
            source_module=source_module,
            source_document_type=source_document_type,
            source_document_id=source_document_id,
        ),
    )
    if enqueue_audit and not result.already_posted:
        OutboxService(db).enqueue(
            tenant_id=ctx.tenant_id,
            event_type="audit.entity_change",
            aggregate_type=source_document_type,
            aggregate_id=source_document_id,
            payload={
                "entity_name": source_document_type,
                "entity_id": str(source_document_id),
                "operation": "finance_post",
                "performed_by": str(ctx.user_id),
                "new_value": {
                    "journal_id": str(result.journal_id),
                    "amount": str(amount),
                    "source_module": source_module,
                },
            },
            idempotency_key=f"audit:{idempotency_key}",
            created_by=ctx.user_id,
        )
    return result.journal_id
