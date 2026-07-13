"""Vendor quotation service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.service.vendor_service import VendorService
from modules.procurement.domain.enums import ProcEntityType, VendorQuotationStatus
from modules.procurement.domain.exceptions import InvalidDocumentState
from modules.procurement.models.vendor_quotation import ProcVendorQuotationHeader
from modules.procurement.repository.rfq_repository import RfqRepository
from modules.procurement.repository.vendor_quotation_repository import VendorQuotationRepository
from modules.procurement.service.document_number_service import DocumentNumberService
from modules.procurement.service.engines.quotation_engine import QuotationEngine
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator


class VendorQuotationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = VendorQuotationRepository(db)
        self._rfqs = RfqRepository(db)
        self._scope = ProcurementScopeValidator(db)
        self._engine = QuotationEngine()
        self._numbers = DocumentNumberService(db)
        self._vendors = VendorService(db)
        self._audit = AuditService(db)

    def list_quotations(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_quotations(ctx, cid)

    def get_quotation(
        self, ctx: TenantContext, quotation_id: UUID
    ) -> ProcVendorQuotationHeader:
        row = self._repo.get_quotation(ctx, quotation_id)
        if row is None:
            raise NotFoundException("Vendor quotation not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        rfq_header_id: UUID,
        vendor_id: UUID,
        document_date,
        valid_until,
        currency_code: str,
        company_id: UUID | None = None,
        exchange_rate: float = 1.0,
        vendor_quote_reference: str | None = None,
        payment_terms: str | None = None,
        delivery_days: int | None = None,
    ):
        rfq = self._rfqs.get_rfq(ctx, rfq_header_id)
        if rfq is None:
            raise NotFoundException("RFQ not found")
        self._scope.validate_company_access(ctx, rfq.company_id)
        self._vendors.get_vendor(ctx, vendor_id)
        cid = self._scope.resolve_company_id(ctx, company_id or rfq.company_id)
        doc_number = self._numbers.generate(
            ProcEntityType.VENDOR_QUOTATION,
            cid,
            model=ProcVendorQuotationHeader,
            code_column="document_number",
        )
        row = self._repo.create_quotation(
            ctx,
            company_id=cid,
            branch_id=rfq.branch_id,
            document_number=doc_number,
            document_date=document_date,
            rfq_header_id=rfq.id,
            vendor_id=vendor_id,
            vendor_quote_reference=vendor_quote_reference,
            valid_until=valid_until,
            payment_terms=payment_terms,
            delivery_days=delivery_days,
            currency_code=currency_code,
            exchange_rate=exchange_rate,
            status=VendorQuotationStatus.DRAFT.value,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="proc_vendor_quotation_header",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

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
        self._engine.validate_submittable(quotation)
        return self._repo.update_quotation(
            ctx,
            quotation_id,
            status=VendorQuotationStatus.SUBMITTED.value,
        )

    def select(self, ctx: TenantContext, quotation_id: UUID):
        quotation = self.get_quotation(ctx, quotation_id)
        if quotation.status not in {
            VendorQuotationStatus.SUBMITTED.value,
            VendorQuotationStatus.UNDER_REVIEW.value,
        }:
            raise InvalidDocumentState("Quotation cannot be selected in its current state")
        return self._repo.update_quotation(
            ctx,
            quotation_id,
            status=VendorQuotationStatus.SELECTED.value,
        )

    def convert_to_order(self, ctx: TenantContext, quotation_id: UUID):
        from modules.procurement.service.order_service import OrderService

        quotation = self.get_quotation(ctx, quotation_id)
        self._engine.validate_convertible(quotation)
        order_svc = OrderService(self._db)
        order = order_svc.create(
            ctx,
            branch_id=quotation.branch_id,
            document_date=quotation.document_date,
            vendor_id=quotation.vendor_id,
            currency_code=quotation.currency_code,
            company_id=quotation.company_id,
            exchange_rate=float(quotation.exchange_rate),
            rfq_header_id=quotation.rfq_header_id,
            vendor_quotation_header_id=quotation.id,
            payment_terms=quotation.payment_terms,
        )
        for line in [ln for ln in quotation.lines if not ln.is_deleted]:
            order_svc.add_line(
                ctx,
                order.id,
                line_number=line.line_number,
                product_id=line.product_id,
                quantity=float(line.quantity),
                uom_id=line.uom_id,
                unit_cost=float(line.unit_cost),
                tax_id=line.tax_id,
                tax_rate=float(line.tax_rate),
            )
        return order_svc.get_order(ctx, order.id)
