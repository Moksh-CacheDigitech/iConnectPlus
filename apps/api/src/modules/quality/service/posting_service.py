"""Quality finance posting via platform IFinancePosting."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.platform.adapters.audit_adapter import AuditAdapter
from modules.platform.dto import AuditIntent
from modules.platform.helpers.system_journal import post_two_line_system_journal
from modules.quality.models import QmCustomerComplaint, QmFinalInspection, QmIncomingInspection


class QualityPostingService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._audit = AuditAdapter(db)

    def _post_pair(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        journal_date,
        description: str,
        fiscal_year_id: UUID | None,
        debit_account_id: UUID,
        credit_account_id: UUID,
        amount: Decimal,
        debit_desc: str,
        credit_desc: str,
        idempotency_key: str,
        source_document_id: UUID,
        source_document_type: str,
    ) -> UUID:
        if amount.quantize(Decimal("0.0001")) <= 0:
            raise ValueError("Posting amount must be positive")
        return post_two_line_system_journal(
            self._db,
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            description=description,
            amount=amount,
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            idempotency_key=idempotency_key,
            source_module="quality",
            source_document_type=source_document_type,
            source_document_id=source_document_id,
            debit_desc=debit_desc,
            credit_desc=credit_desc,
            journal_date=journal_date,
            fiscal_year_id=fiscal_year_id,
        )

    def post_quality_cost(
        self,
        ctx: TenantContext,
        doc: QmIncomingInspection | QmFinalInspection,
        *,
        amount: Decimal,
        quality_expense_account_id: UUID,
        inventory_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        jid = self._post_pair(
            ctx,
            company_id=doc.company_id,
            branch_id=doc.branch_id,
            journal_date=doc.document_date,
            description=f"QM quality cost {getattr(doc, 'document_number', doc.id)}",
            fiscal_year_id=fiscal_year_id,
            debit_account_id=quality_expense_account_id,
            credit_account_id=inventory_account_id,
            amount=amount,
            debit_desc="Quality expense",
            credit_desc="Inventory offset",
            idempotency_key=f"quality.cost:{doc.id}",
            source_document_id=doc.id,
            source_document_type="quality_inspection",
        )
        self._audit.log_entity_change(
            AuditIntent(
                tenant_id=ctx.tenant_id,
                entity_name="quality_inspection",
                entity_id=doc.id,
                operation="finance_post",
                performed_by=ctx.user_id,
                new_value={"journal_id": str(jid)},
            )
        )
        return jid

    def post_complaint_cost(
        self,
        ctx: TenantContext,
        doc: QmCustomerComplaint,
        *,
        amount: Decimal,
        quality_expense_account_id: UUID,
        liability_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        return self._post_pair(
            ctx,
            company_id=doc.company_id,
            branch_id=doc.branch_id,
            journal_date=doc.document_date,
            description=f"QM complaint {getattr(doc, 'document_number', doc.id)}",
            fiscal_year_id=fiscal_year_id,
            debit_account_id=quality_expense_account_id,
            credit_account_id=liability_account_id,
            amount=amount,
            debit_desc="Complaint expense",
            credit_desc="Complaint liability",
            idempotency_key=f"quality.complaint:{doc.id}",
            source_document_id=doc.id,
            source_document_type="quality_complaint",
        )
