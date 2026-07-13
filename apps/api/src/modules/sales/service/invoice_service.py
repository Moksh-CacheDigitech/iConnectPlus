"""Sales invoice service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.finance.repository.fiscal_repository import FiscalRepository
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.sales.domain.enums import DeliveryStatus, InvoiceStatus, SalesEntityType
from modules.sales.domain.exceptions import InvalidDocumentState, SegregationOfDutiesError
from modules.sales.models.invoice import SalesInvoiceHeader
from modules.sales.repository.delivery_repository import DeliveryRepository
from modules.sales.repository.invoice_repository import InvoiceRepository
from modules.sales.repository.order_repository import OrderRepository
from modules.sales.service.document_number_service import DocumentNumberService
from modules.sales.service.engines.invoice_engine import InvoiceEngine
from modules.sales.service.engines.order_engine import OrderEngine
from modules.sales.service.governance_service import SalesGovernanceService
from modules.sales.service.sales_scope_validator import SalesScopeValidator


class InvoiceService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = InvoiceRepository(db)
        self._deliveries = DeliveryRepository(db)
        self._orders = OrderRepository(db)
        self._fiscal = FiscalRepository(db)
        self._scope = SalesScopeValidator(db)
        self._engine = InvoiceEngine()
        self._order_engine = OrderEngine()
        self._numbers = DocumentNumberService(db)
        self._governance = SalesGovernanceService(db)
        self._audit = AuditService(db)

    def list_invoices(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_invoices(ctx, cid)

    def get_invoice(self, ctx: TenantContext, invoice_id: UUID) -> SalesInvoiceHeader:
        row = self._repo.get_invoice(ctx, invoice_id)
        if row is None:
            raise NotFoundException("Invoice not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create_from_delivery(
        self,
        ctx: TenantContext,
        *,
        delivery_header_id: UUID,
        document_date,
        due_date,
        period_id: UUID | None = None,
        company_id: UUID | None = None,
    ):
        delivery = self._deliveries.get_delivery(ctx, delivery_header_id)
        if delivery is None:
            raise NotFoundException("Delivery not found")
        if delivery.status != DeliveryStatus.DELIVERED.value:
            raise InvalidDocumentState("Only shipped deliveries can be invoiced")
        self._scope.validate_company_access(ctx, delivery.company_id)
        order = self._orders.get_order(ctx, delivery.order_header_id)
        if order is None:
            raise NotFoundException("Sales order not found")

        cid = self._scope.resolve_company_id(ctx, company_id or delivery.company_id)
        if period_id is None:
            period = self._fiscal.get_period_for_date(ctx, cid, document_date)
            if period is None:
                raise NotFoundException("No open period for invoice date")
            period_id = period.id
            fiscal_year_id = period.fiscal_year_id
        else:
            period = self._fiscal.get_period(ctx, period_id)
            if period is None:
                raise NotFoundException("Period not found")
            fiscal_year_id = period.fiscal_year_id

        doc_number = self._numbers.generate(
            SalesEntityType.INVOICE,
            cid,
            model=SalesInvoiceHeader,
            code_column="document_number",
        )
        invoice = self._repo.create_invoice(
            ctx,
            company_id=cid,
            branch_id=delivery.branch_id,
            document_number=doc_number,
            document_date=document_date,
            due_date=due_date,
            customer_id=delivery.customer_id,
            order_header_id=order.id,
            delivery_header_id=delivery.id,
            fiscal_year_id=fiscal_year_id,
            period_id=period_id,
            currency_code=order.currency_code,
            exchange_rate=float(order.exchange_rate),
            status=InvoiceStatus.DRAFT.value,
            workflow_status=WorkflowStatus.PENDING.value,
        )
        order_lines = {ln.id: ln for ln in order.lines}
        line_number = 1
        for dline in [ln for ln in delivery.lines if not ln.is_deleted]:
            order_line = order_lines.get(dline.order_line_id)
            if order_line is None:
                continue
            inv_line = self._repo.add_line(
                ctx,
                invoice,
                order_line_id=order_line.id,
                delivery_line_id=dline.id,
                line_number=line_number,
                product_id=order_line.product_id,
                product_code=order_line.product_code,
                quantity=float(dline.quantity),
                uom_id=order_line.uom_id,
                unit_price=float(order_line.unit_price),
                discount_amount=0,
                tax_id=order_line.tax_id,
                tax_rate=float(order_line.tax_rate),
            )
            totals = self._engine.compute_line_totals(inv_line)
            self._engine.apply_line_totals(inv_line, totals)
            self._order_engine.apply_invoice_qty(order_line, Decimal(str(dline.quantity)))
            line_number += 1

        invoice = self.get_invoice(ctx, invoice.id)
        header_totals = self._engine.compute_header_totals(invoice.lines)
        self._engine.apply_header_totals(invoice, header_totals)
        self._order_engine.refresh_header_amounts(order)
        self._db.flush()
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_invoice_header",
            entity_id=invoice.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return invoice

    def submit(self, ctx: TenantContext, invoice_id: UUID):
        invoice = self.get_invoice(ctx, invoice_id)
        if invoice.status != InvoiceStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft invoices can be submitted")
        instance = self._governance.submit_for_approval(
            ctx, entity_name="sales_invoice_header", entity_id=invoice_id
        )
        return self._repo.update_invoice(
            ctx,
            invoice_id,
            status=InvoiceStatus.SUBMITTED.value,
            workflow_status=WorkflowStatus.IN_PROGRESS.value,
            workflow_instance_id=instance.id,
        )

    def approve(self, ctx: TenantContext, invoice_id: UUID):
        invoice = self.get_invoice(ctx, invoice_id)
        if invoice.created_by == ctx.user_id:
            raise SegregationOfDutiesError("Creator cannot approve own invoice")
        if invoice.workflow_instance_id is None:
            raise InvalidDocumentState("Invoice has no workflow instance")

        def on_approved():
            self._repo.update_invoice(
                ctx,
                invoice_id,
                workflow_status=WorkflowStatus.APPROVED.value,
            )

        return self._governance.approve(
            ctx,
            instance_id=invoice.workflow_instance_id,
            entity_name="sales_invoice_header",
            entity_id=invoice_id,
            on_approved=on_approved,
        )

    def cancel(self, ctx: TenantContext, invoice_id: UUID):
        invoice = self.get_invoice(ctx, invoice_id)
        if invoice.status == InvoiceStatus.POSTED.value:
            raise InvalidDocumentState("Posted invoices cannot be cancelled")
        return self._repo.update_invoice(ctx, invoice_id, status=InvoiceStatus.CANCELLED.value)
