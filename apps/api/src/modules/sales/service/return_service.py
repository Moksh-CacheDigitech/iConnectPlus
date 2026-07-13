"""Sales return service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.finance.repository.fiscal_repository import FiscalRepository
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.inventory.adapters.sales_adapter import SalesInventoryAdapter
from modules.sales.domain.enums import ReturnStatus, SalesEntityType
from modules.sales.domain.exceptions import InvalidDocumentState, SegregationOfDutiesError
from modules.sales.models.return_doc import SalesReturnHeader
from modules.sales.repository.invoice_repository import InvoiceRepository
from modules.sales.repository.order_repository import OrderRepository
from modules.sales.repository.return_repository import ReturnRepository
from modules.sales.service.document_number_service import DocumentNumberService
from modules.sales.service.engines.return_engine import ReturnEngine
from modules.sales.service.governance_service import SalesGovernanceService
from modules.sales.service.sales_scope_validator import SalesScopeValidator


class ReturnService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ReturnRepository(db)
        self._invoices = InvoiceRepository(db)
        self._orders = OrderRepository(db)
        self._fiscal = FiscalRepository(db)
        self._scope = SalesScopeValidator(db)
        self._engine = ReturnEngine()
        self._numbers = DocumentNumberService(db)
        self._governance = SalesGovernanceService(db)
        self._inventory = SalesInventoryAdapter(db)
        self._audit = AuditService(db)

    def list_returns(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_returns(ctx, cid)

    def get_return(self, ctx: TenantContext, return_id: UUID) -> SalesReturnHeader:
        row = self._repo.get_return(ctx, return_id)
        if row is None:
            raise NotFoundException("Return not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        document_date,
        customer_id: UUID,
        return_type: str,
        currency_code: str,
        company_id: UUID | None = None,
        invoice_header_id: UUID | None = None,
        order_header_id: UUID | None = None,
        period_id: UUID | None = None,
        exchange_rate: float = 1.0,
        reason: str | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        if invoice_header_id:
            invoice = self._invoices.get_invoice(ctx, invoice_header_id)
            if invoice is None:
                raise NotFoundException("Invoice not found")
            self._engine.validate_invoice_for_return(invoice)

        if period_id is None:
            period = self._fiscal.get_period_for_date(ctx, cid, document_date)
            if period is None:
                raise NotFoundException("No open period for return date")
            period_id = period.id
            fiscal_year_id = period.fiscal_year_id
        else:
            period = self._fiscal.get_period(ctx, period_id)
            if period is None:
                raise NotFoundException("Period not found")
            fiscal_year_id = period.fiscal_year_id

        doc_number = self._numbers.generate(
            SalesEntityType.RETURN,
            cid,
            model=SalesReturnHeader,
            code_column="document_number",
        )
        row = self._repo.create_return(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            document_number=doc_number,
            document_date=document_date,
            customer_id=customer_id,
            invoice_header_id=invoice_header_id,
            order_header_id=order_header_id,
            fiscal_year_id=fiscal_year_id,
            period_id=period_id,
            return_type=return_type,
            currency_code=currency_code,
            exchange_rate=exchange_rate,
            reason=reason,
            status=ReturnStatus.DRAFT.value,
            workflow_status=WorkflowStatus.PENDING.value,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_return_header",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def add_line(self, ctx: TenantContext, return_id: UUID, **fields):
        header = self.get_return(ctx, return_id)
        if header.status != ReturnStatus.DRAFT.value:
            raise InvalidDocumentState("Lines can only be added to draft returns")
        line = self._repo.add_line(ctx, header, status="requested", **fields)
        if fields.get("invoice_line_id") and header.invoice_header_id:
            invoice = self._invoices.get_invoice(ctx, header.invoice_header_id)
            if invoice is None:
                raise NotFoundException("Invoice not found")
            inv_line = next(
                (
                    ln
                    for ln in invoice.lines
                    if ln.id == fields["invoice_line_id"]
                ),
                None,
            )
            if inv_line is None:
                raise NotFoundException("Invoice line not found")
            self._engine.validate_against_invoice_line(line, inv_line)
        self._engine.apply_header_totals(header)
        self._db.flush()
        return line

    def submit(self, ctx: TenantContext, return_id: UUID):
        header = self.get_return(ctx, return_id)
        self._engine.validate_submittable(header)
        instance = self._governance.submit_for_approval(
            ctx, entity_name="sales_return_header", entity_id=return_id
        )
        return self._repo.update_return(
            ctx,
            return_id,
            status=ReturnStatus.REQUESTED.value,
            workflow_status=WorkflowStatus.IN_PROGRESS.value,
            workflow_instance_id=instance.id,
        )

    def approve(self, ctx: TenantContext, return_id: UUID):
        header = self.get_return(ctx, return_id)
        if header.created_by == ctx.user_id:
            raise SegregationOfDutiesError("Creator cannot approve own return")
        if header.workflow_instance_id is None:
            raise InvalidDocumentState("Return has no workflow instance")

        def on_approved():
            self._repo.update_return(
                ctx,
                return_id,
                status=ReturnStatus.APPROVED.value,
                workflow_status=WorkflowStatus.APPROVED.value,
            )

        return self._governance.approve(
            ctx,
            instance_id=header.workflow_instance_id,
            entity_name="sales_return_header",
            entity_id=return_id,
            on_approved=on_approved,
        )

    def receive(self, ctx: TenantContext, return_id: UUID, *, warehouse_id: UUID | None = None):
        header = self.get_return(ctx, return_id)
        if header.status != ReturnStatus.APPROVED.value:
            raise InvalidDocumentState("Only approved returns can be received")
        for line in [ln for ln in header.lines if not ln.is_deleted]:
            line.status = "received"
            if line.order_line_id:
                order_line = self._orders.get_line(ctx, line.order_line_id)
                if order_line:
                    self._engine.apply_return_to_order_line(
                        order_line, Decimal(str(line.quantity))
                    )
        if warehouse_id is not None:
            self._inventory.receive_return(ctx, return_id, warehouse_id)
        return self._repo.update_return(ctx, return_id, status=ReturnStatus.RECEIVED.value)
