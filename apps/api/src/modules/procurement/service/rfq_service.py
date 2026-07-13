"""RFQ service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.procurement.domain.enums import ProcEntityType, RfqStatus
from modules.procurement.domain.exceptions import InvalidDocumentState, SegregationOfDutiesError
from modules.procurement.models.rfq import ProcRfqHeader
from modules.procurement.repository.requisition_repository import RequisitionRepository
from modules.procurement.repository.rfq_repository import RfqRepository
from modules.procurement.service.document_number_service import DocumentNumberService
from modules.procurement.service.engines.rfq_engine import RfqEngine
from modules.procurement.service.governance_service import ProcurementGovernanceService
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator


class RfqService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = RfqRepository(db)
        self._requisitions = RequisitionRepository(db)
        self._scope = ProcurementScopeValidator(db)
        self._engine = RfqEngine()
        self._numbers = DocumentNumberService(db)
        self._governance = ProcurementGovernanceService(db)
        self._audit = AuditService(db)

    def list_rfqs(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rfqs(ctx, cid)

    def get_rfq(self, ctx: TenantContext, rfq_id: UUID) -> ProcRfqHeader:
        row = self._repo.get_rfq(ctx, rfq_id)
        if row is None:
            raise NotFoundException("RFQ not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create_from_requisition(
        self,
        ctx: TenantContext,
        *,
        requisition_id: UUID,
        closing_date,
        company_id: UUID | None = None,
    ):
        requisition = self._requisitions.get_requisition(ctx, requisition_id)
        if requisition is None:
            raise NotFoundException("Requisition not found")
        self._engine.validate_from_requisition(requisition)
        cid = self._scope.resolve_company_id(ctx, company_id or requisition.company_id)
        doc_number = self._numbers.generate(
            ProcEntityType.RFQ,
            cid,
            model=ProcRfqHeader,
            code_column="document_number",
        )
        rfq = self._repo.create_rfq(
            ctx,
            company_id=cid,
            branch_id=requisition.branch_id,
            document_number=doc_number,
            document_date=requisition.document_date,
            requisition_header_id=requisition.id,
            closing_date=closing_date,
            currency_code=requisition.currency_code,
            exchange_rate=float(requisition.exchange_rate),
            status=RfqStatus.DRAFT.value,
            workflow_status=WorkflowStatus.PENDING.value,
        )
        line_number = 1
        for req_line in [ln for ln in requisition.lines if not ln.is_deleted]:
            self._repo.add_line(
                ctx,
                rfq,
                requisition_line_id=req_line.id,
                line_number=line_number,
                product_id=req_line.product_id,
                quantity=float(req_line.quantity),
                uom_id=req_line.uom_id,
                target_unit_cost=float(req_line.estimated_unit_cost or 0),
            )
            line_number += 1
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="proc_rfq_header",
            entity_id=rfq.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return self.get_rfq(ctx, rfq.id)

    def add_vendor(self, ctx: TenantContext, rfq_id: UUID, *, vendor_id: UUID):
        rfq = self.get_rfq(ctx, rfq_id)
        self._engine.validate_editable(rfq)
        return self._repo.add_vendor(ctx, rfq, vendor_id=vendor_id)

    def publish(self, ctx: TenantContext, rfq_id: UUID):
        rfq = self.get_rfq(ctx, rfq_id)
        self._engine.validate_publishable(rfq)
        return self._repo.update_rfq(ctx, rfq_id, status=RfqStatus.PUBLISHED.value)

    def submit(self, ctx: TenantContext, rfq_id: UUID):
        rfq = self.get_rfq(ctx, rfq_id)
        if rfq.status != RfqStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft RFQs can be submitted")
        instance = self._governance.submit_for_approval(
            ctx, entity_name="proc_rfq_header", entity_id=rfq_id
        )
        return self._repo.update_rfq(
            ctx,
            rfq_id,
            workflow_status=WorkflowStatus.IN_PROGRESS.value,
            workflow_instance_id=instance.id,
        )

    def approve(self, ctx: TenantContext, rfq_id: UUID):
        rfq = self.get_rfq(ctx, rfq_id)
        if rfq.created_by == ctx.user_id:
            raise SegregationOfDutiesError("Creator cannot approve own RFQ")
        if rfq.workflow_instance_id is None:
            raise InvalidDocumentState("RFQ has no workflow instance")

        def on_approved():
            self._repo.update_rfq(
                ctx,
                rfq_id,
                workflow_status=WorkflowStatus.APPROVED.value,
            )

        return self._governance.approve(
            ctx,
            instance_id=rfq.workflow_instance_id,
            entity_name="proc_rfq_header",
            entity_id=rfq_id,
            on_approved=on_approved,
        )

    def close(self, ctx: TenantContext, rfq_id: UUID):
        rfq = self.get_rfq(ctx, rfq_id)
        if rfq.status == RfqStatus.CANCELLED.value:
            raise InvalidDocumentState("RFQ is already cancelled")
        return self._repo.update_rfq(ctx, rfq_id, status=RfqStatus.CLOSED.value)
