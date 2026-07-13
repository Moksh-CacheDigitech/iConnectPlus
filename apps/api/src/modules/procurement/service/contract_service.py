"""Vendor contract service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.procurement.domain.enums import ContractStatus, ProcEntityType
from modules.procurement.domain.exceptions import InvalidDocumentState, SegregationOfDutiesError
from modules.procurement.models.contract import ProcVendorContract
from modules.procurement.repository.contract_repository import ContractRepository
from modules.procurement.service.document_number_service import DocumentNumberService
from modules.procurement.service.engines.contract_engine import ContractEngine
from modules.procurement.service.governance_service import ProcurementGovernanceService
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator


class ContractService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ContractRepository(db)
        self._scope = ProcurementScopeValidator(db)
        self._engine = ContractEngine()
        self._numbers = DocumentNumberService(db)
        self._governance = ProcurementGovernanceService(db)
        self._audit = AuditService(db)

    def list_contracts(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_contracts(ctx, cid)

    def get_contract(self, ctx: TenantContext, contract_id: UUID) -> ProcVendorContract:
        row = self._repo.get_contract(ctx, contract_id)
        if row is None:
            raise NotFoundException("Contract not found")
        self._scope.validate_company_access(ctx, row.company_id)
        if row.branch_id:
            self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        vendor_id: UUID,
        contract_name: str,
        start_date,
        end_date,
        currency_code: str,
        company_id: UUID | None = None,
        branch_id: UUID | None = None,
        contract_value: float | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        if branch_id:
            self._scope.validate_branch_access(ctx, branch_id)
        doc_number = self._numbers.generate(
            ProcEntityType.CONTRACT,
            cid,
            model=ProcVendorContract,
            code_column="document_number",
        )
        row = self._repo.create_contract(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            document_number=doc_number,
            vendor_id=vendor_id,
            contract_name=contract_name,
            start_date=start_date,
            end_date=end_date,
            contract_value=contract_value,
            currency_code=currency_code,
            status=ContractStatus.DRAFT.value,
            workflow_status=WorkflowStatus.PENDING.value,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="proc_vendor_contract",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def add_line(self, ctx: TenantContext, contract_id: UUID, **fields):
        contract = self.get_contract(ctx, contract_id)
        self._engine.validate_editable(contract)
        line = self._repo.add_line(ctx, contract, **fields)
        self._db.flush()
        return line

    def submit(self, ctx: TenantContext, contract_id: UUID):
        contract = self.get_contract(ctx, contract_id)
        if contract.status != ContractStatus.DRAFT.value:
            raise InvalidDocumentState("Only draft contracts can be submitted")
        instance = self._governance.submit_for_approval(
            ctx, entity_name="proc_vendor_contract", entity_id=contract_id
        )
        return self._repo.update_contract(
            ctx,
            contract_id,
            workflow_status=WorkflowStatus.IN_PROGRESS.value,
            workflow_instance_id=instance.id,
        )

    def approve(self, ctx: TenantContext, contract_id: UUID):
        contract = self.get_contract(ctx, contract_id)
        if contract.created_by == ctx.user_id:
            raise SegregationOfDutiesError("Creator cannot approve own contract")
        if contract.workflow_instance_id is None:
            raise InvalidDocumentState("Contract has no workflow instance")

        def on_approved():
            self._engine.validate_activatable(contract)
            self._repo.update_contract(
                ctx,
                contract_id,
                status=ContractStatus.ACTIVE.value,
                workflow_status=WorkflowStatus.APPROVED.value,
            )

        return self._governance.approve(
            ctx,
            instance_id=contract.workflow_instance_id,
            entity_name="proc_vendor_contract",
            entity_id=contract_id,
            on_approved=on_approved,
        )

    def terminate(self, ctx: TenantContext, contract_id: UUID):
        contract = self.get_contract(ctx, contract_id)
        if contract.status != ContractStatus.ACTIVE.value:
            raise InvalidDocumentState("Only active contracts can be terminated")
        return self._repo.update_contract(
            ctx, contract_id, status=ContractStatus.TERMINATED.value
        )
