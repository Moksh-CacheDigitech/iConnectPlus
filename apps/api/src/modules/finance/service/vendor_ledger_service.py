"""Vendor ledger (AP) service."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.finance.domain.enums import FinanceEntityType
from modules.finance.models.ledger import FinVendorLedger
from modules.finance.repository.subledger_repository import SubLedgerRepository
from modules.finance.service.document_number_service import DocumentNumberService
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class VendorLedgerService:
    def __init__(self, db: Session) -> None:
        self._repo = SubLedgerRepository(db)
        self._scope = FinanceScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._audit = AuditService(db)

    def list_entries(self, ctx: TenantContext, company_id: UUID | None = None, vendor_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_vendor_ledger(ctx, cid, vendor_id)

    def create_entry(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID,
        vendor_id: UUID,
        document_date: date,
        due_date: date,
        document_type: str,
        credit_amount: float = 0,
        debit_amount: float = 0,
        currency_code: str = "INR",
        exchange_rate: float = 1.0,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc_number = self._numbers.generate(
            FinanceEntityType.VENDOR_LEDGER,
            cid,
            model=FinVendorLedger,
            code_column="document_number",
        )
        balance = credit_amount - debit_amount
        entry = self._repo.create_vendor_entry(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            vendor_id=vendor_id,
            document_number=doc_number,
            document_date=document_date,
            due_date=due_date,
            document_type=document_type,
            credit_amount=credit_amount,
            debit_amount=debit_amount,
            balance_amount=balance,
            currency_code=currency_code,
            exchange_rate=exchange_rate,
            status="open",
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_vendor_ledger",
            entity_id=entry.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return entry

    def record_payment(self, ctx: TenantContext, entry_id: UUID, payment_amount: float):
        entry = self._repo.get_vendor_entry(ctx, entry_id)
        if entry is None:
            raise NotFoundException("AP entry not found")
        new_balance = float(entry.balance_amount) - payment_amount
        status = "paid" if new_balance <= 0 else "partial"
        return self._repo.update_vendor_entry(
            ctx,
            entry_id,
            debit_amount=float(entry.debit_amount) + payment_amount,
            balance_amount=max(new_balance, 0),
            status=status,
        )

    def aging_report(self, ctx: TenantContext, company_id: UUID | None = None, as_of: date | None = None):
        from datetime import date as date_cls

        cid = self._scope.resolve_company_id(ctx, company_id)
        as_of_date = as_of or date_cls.today()
        entries = self._repo.list_open_ap_for_aging(ctx, cid)
        for entry in entries:
            entry.aging_bucket = self._repo.compute_aging_bucket(entry.due_date, as_of_date)
        return entries
