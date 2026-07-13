"""Purchase requisition service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.procurement.domain.enums import ProcEntityType, RequisitionStatus
from modules.procurement.domain.exceptions import InvalidDocumentState, SegregationOfDutiesError
from modules.procurement.models.requisition import ProcRequisitionHeader
from modules.procurement.repository.requisition_repository import RequisitionRepository
from modules.procurement.service.document_number_service import DocumentNumberService
from modules.procurement.service.engines.requisition_engine import RequisitionEngine
from modules.procurement.service.governance_service import ProcurementGovernanceService
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator


class RequisitionService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = RequisitionRepository(db)
        self._scope = ProcurementScopeValidator(db)
        self._engine = RequisitionEngine()
        self._numbers = DocumentNumberService(db)
        self._governance = ProcurementGovernanceService(db)
        self._audit = AuditService(db)

    def list_requisitions(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_requisitions(ctx, cid)

    def get_requisition(
        self, ctx: TenantContext, requisition_id: UUID
    ) -> ProcRequisitionHeader:
        row = self._repo.get_requisition(ctx, requisition_id)
        if row is None:
            raise NotFoundException("Requisition not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        document_date,
        requester_id: UUID,
        department_id: UUID,
        cost_center_id: UUID,
        required_date,
        currency_code: str,
        company_id: UUID | None = None,
        exchange_rate: float = 1.0,
        priority: str = "medium",
        notes: str | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc_number = self._numbers.generate(
            ProcEntityType.REQUISITION,
            cid,
            model=ProcRequisitionHeader,
            code_column="document_number",
        )
        row = self._repo.create_requisition(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            document_number=doc_number,
            document_date=document_date,
            requester_id=requester_id,
            department_id=department_id,
            cost_center_id=cost_center_id,
            required_date=required_date,
            currency_code=currency_code,
            exchange_rate=exchange_rate,
            priority=priority,
            notes=notes,
            status=RequisitionStatus.DRAFT.value,
            workflow_status=WorkflowStatus.PENDING.value,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="proc_requisition_header",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, requisition_id: UUID, **fields):
        requisition = self.get_requisition(ctx, requisition_id)
        self._engine.validate_editable(requisition)
        updated = self._repo.update_requisition(ctx, requisition_id, **fields)
        if updated is None:
            raise NotFoundException("Requisition not found")
        return updated

    def add_line(self, ctx: TenantContext, requisition_id: UUID, **fields):
        requisition = self.get_requisition(ctx, requisition_id)
        self._engine.validate_editable(requisition)
        line = self._repo.add_line(
            ctx,
            requisition_id,
            company_id=requisition.company_id,
            branch_id=requisition.branch_id,
            **fields,
        )
        totals = self._engine.compute_line_totals(line)
        self._engine.apply_line_totals(line, totals)
        requisition = self.get_requisition(ctx, requisition_id)
        header_totals = self._engine.compute_header_totals(requisition.lines)
        self._engine.apply_header_totals(requisition, header_totals)
        self._db.flush()
        return line

    def submit(self, ctx: TenantContext, requisition_id: UUID):
        requisition = self.get_requisition(ctx, requisition_id)
        self._engine.validate_submittable(requisition)
        instance = self._governance.submit_for_approval(
            ctx, entity_name="proc_requisition_header", entity_id=requisition_id
        )
        return self._repo.update_requisition(
            ctx,
            requisition_id,
            status=RequisitionStatus.SUBMITTED.value,
            workflow_status=WorkflowStatus.IN_PROGRESS.value,
            workflow_instance_id=instance.id,
        )

    def approve(self, ctx: TenantContext, requisition_id: UUID):
        requisition = self.get_requisition(ctx, requisition_id)
        if requisition.created_by == ctx.user_id:
            raise SegregationOfDutiesError("Creator cannot approve own requisition")
        if requisition.workflow_instance_id is None:
            raise InvalidDocumentState("Requisition has no workflow instance")

        def on_approved():
            self._repo.update_requisition(
                ctx,
                requisition_id,
                status=RequisitionStatus.APPROVED.value,
                workflow_status=WorkflowStatus.APPROVED.value,
            )

        return self._governance.approve(
            ctx,
            instance_id=requisition.workflow_instance_id,
            entity_name="proc_requisition_header",
            entity_id=requisition_id,
            on_approved=on_approved,
        )

    def reject(self, ctx: TenantContext, requisition_id: UUID):
        requisition = self.get_requisition(ctx, requisition_id)
        if requisition.workflow_instance_id is None:
            raise InvalidDocumentState("Requisition has no workflow instance")

        def on_rejected():
            self._repo.update_requisition(
                ctx,
                requisition_id,
                status=RequisitionStatus.REJECTED.value,
                workflow_status=WorkflowStatus.REJECTED.value,
            )

        return self._governance.reject(
            ctx,
            instance_id=requisition.workflow_instance_id,
            entity_name="proc_requisition_header",
            entity_id=requisition_id,
            on_rejected=on_rejected,
        )

    def convert_to_rfq(self, ctx: TenantContext, requisition_id: UUID):
        from modules.procurement.service.rfq_service import RfqService

        requisition = self.get_requisition(ctx, requisition_id)
        self._engine.validate_convertible(requisition)
        rfq_svc = RfqService(self._db)
        rfq = rfq_svc.create_from_requisition(
            ctx,
            requisition_id=requisition.id,
            closing_date=requisition.required_date,
        )
        self._repo.update_requisition(
            ctx,
            requisition_id,
            status=RequisitionStatus.CONVERTED_TO_RFQ.value,
        )
        return rfq
