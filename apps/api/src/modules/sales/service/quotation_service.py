"""Quotation service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.service.customer_service import CustomerService
from modules.sales.domain.enums import QuotationStatus, SalesEntityType
from modules.sales.domain.exceptions import InvalidDocumentState, SegregationOfDutiesError
from modules.sales.models.quotation import SalesQuotationHeader
from modules.sales.repository.quotation_repository import QuotationRepository
from modules.sales.service.document_number_service import DocumentNumberService
from modules.sales.service.engines.quotation_engine import QuotationEngine
from modules.sales.service.governance_service import SalesGovernanceService
from modules.sales.service.sales_scope_validator import SalesScopeValidator


class QuotationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = QuotationRepository(db)
        self._scope = SalesScopeValidator(db)
        self._engine = QuotationEngine()
        self._numbers = DocumentNumberService(db)
        self._governance = SalesGovernanceService(db)
        self._customers = CustomerService(db)
        self._audit = AuditService(db)

    def list_quotations(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_quotations(ctx, cid)

    def get_quotation(self, ctx: TenantContext, quotation_id: UUID) -> SalesQuotationHeader:
        row = self._repo.get_quotation(ctx, quotation_id)
        if row is None:
            raise NotFoundException("Quotation not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        document_date,
        valid_until,
        customer_id: UUID,
        currency_code: str,
        company_id: UUID | None = None,
        exchange_rate: float = 1.0,
        payment_terms: str | None = None,
        opportunity_reference: UUID | None = None,
        price_list_id: UUID | None = None,
        notes: str | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        customer = self._customers.get_customer(ctx, customer_id)
        doc_number = self._numbers.generate(
            SalesEntityType.QUOTATION,
            cid,
            model=SalesQuotationHeader,
            code_column="document_number",
        )
        row = self._repo.create_quotation(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            document_number=doc_number,
            document_date=document_date,
            valid_until=valid_until,
            customer_id=customer_id,
            customer_name=customer.customer_name,
            currency_code=currency_code,
            exchange_rate=exchange_rate,
            payment_terms=payment_terms,
            opportunity_reference=opportunity_reference,
            price_list_id=price_list_id,
            notes=notes,
            status=QuotationStatus.DRAFT.value,
            workflow_status=WorkflowStatus.PENDING.value,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_quotation_header",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, quotation_id: UUID, **fields):
        quotation = self.get_quotation(ctx, quotation_id)
        self._engine.validate_editable(quotation)
        updated = self._repo.update_quotation(ctx, quotation_id, **fields)
        if updated is None:
            raise NotFoundException("Quotation not found")
        return updated

    def delete(self, ctx: TenantContext, quotation_id: UUID) -> None:
        quotation = self.get_quotation(ctx, quotation_id)
        self._engine.validate_editable(quotation)
        if not self._repo.soft_delete_quotation(ctx, quotation_id):
            raise NotFoundException("Quotation not found")

    def add_line(self, ctx: TenantContext, quotation_id: UUID, **fields):
        quotation = self.get_quotation(ctx, quotation_id)
        self._engine.validate_editable(quotation)
        line = self._repo.add_line(ctx, quotation, **fields)
        totals = self._engine.compute_line_totals(line)
        self._engine.apply_line_totals(line, totals)
        quotation = self.get_quotation(ctx, quotation_id)
        header_totals = self._engine.compute_header_totals(quotation.lines)
        self._engine.apply_header_totals(quotation, header_totals)
        self._db.flush()
        return line

    def submit(self, ctx: TenantContext, quotation_id: UUID):
        quotation = self.get_quotation(ctx, quotation_id)
        if quotation.status != QuotationStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft quotations can be submitted")
        if not quotation.lines:
            raise InvalidDocumentState("Quotation must have at least one line")
        instance = self._governance.submit_for_approval(
            ctx, entity_name="sales_quotation_header", entity_id=quotation_id
        )
        return self._repo.update_quotation(
            ctx,
            quotation_id,
            status=QuotationStatus.SUBMITTED.value,
            workflow_status=WorkflowStatus.IN_PROGRESS.value,
            workflow_instance_id=instance.id,
        )

    def approve(self, ctx: TenantContext, quotation_id: UUID):
        quotation = self.get_quotation(ctx, quotation_id)
        if quotation.created_by == ctx.user_id:
            raise SegregationOfDutiesError("Creator cannot approve own quotation")
        if quotation.workflow_instance_id is None:
            raise InvalidDocumentState("Quotation has no workflow instance")

        def on_approved():
            self._repo.update_quotation(
                ctx,
                quotation_id,
                status=QuotationStatus.ACCEPTED.value,
                workflow_status=WorkflowStatus.APPROVED.value,
            )

        return self._governance.approve(
            ctx,
            instance_id=quotation.workflow_instance_id,
            entity_name="sales_quotation_header",
            entity_id=quotation_id,
            on_approved=on_approved,
        )

    def reject(self, ctx: TenantContext, quotation_id: UUID):
        quotation = self.get_quotation(ctx, quotation_id)
        if quotation.workflow_instance_id is None:
            raise InvalidDocumentState("Quotation has no workflow instance")

        def on_rejected():
            self._repo.update_quotation(
                ctx,
                quotation_id,
                status=QuotationStatus.REJECTED.value,
                workflow_status=WorkflowStatus.REJECTED.value,
            )

        return self._governance.reject(
            ctx,
            instance_id=quotation.workflow_instance_id,
            entity_name="sales_quotation_header",
            entity_id=quotation_id,
            on_rejected=on_rejected,
        )

    def convert_to_order(self, ctx: TenantContext, quotation_id: UUID):
        from modules.sales.service.sales_order_service import SalesOrderService

        quotation = self.get_quotation(ctx, quotation_id)
        self._engine.validate_convertible(quotation)
        order_svc = SalesOrderService(self._db)
        order = order_svc.create(
            ctx,
            branch_id=quotation.branch_id,
            document_date=quotation.document_date,
            customer_id=quotation.customer_id,
            currency_code=quotation.currency_code,
            company_id=quotation.company_id,
            exchange_rate=float(quotation.exchange_rate),
            quotation_header_id=quotation.id,
            price_list_id=quotation.price_list_id,
        )
        for line in [ln for ln in quotation.lines if not ln.is_deleted]:
            order_svc.add_line(
                ctx,
                order.id,
                line_number=line.line_number,
                product_id=line.product_id,
                product_code=line.product_code,
                product_name=line.product_name,
                quantity=float(line.quantity),
                uom_id=line.uom_id,
                unit_price=float(line.unit_price),
                quotation_line_id=line.id,
                discount_percent=float(line.discount_percent),
                discount_amount=float(line.discount_amount),
                tax_id=line.tax_id,
                tax_rate=float(line.tax_rate),
            )
        return order_svc.get_order(ctx, order.id)
