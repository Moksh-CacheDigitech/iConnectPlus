"""IWorkflow → Foundation WorkflowService."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.exceptions import WorkflowStateException
from modules.foundation.service.workflow_service import WorkflowService
from modules.platform.compat.audit_facade import PlatformAuditFacade
from modules.platform.dto import WorkflowActionRequest, WorkflowStartRequest


class WorkflowAdapter:
    def __init__(self, db: Session) -> None:
        self._wf = WorkflowService(db)
        self._db = db
        self._audit = PlatformAuditFacade(db)

    def get_definition_id(self, tenant_id: UUID, workflow_code: str) -> UUID | None:
        for definition in self._wf.list_definitions(tenant_id):
            if getattr(definition, "workflow_code", None) == workflow_code:
                return definition.id
        return None

    def start(self, request: WorkflowStartRequest):
        definition_id = self.get_definition_id(request.tenant_id, request.workflow_code)
        if definition_id is None:
            raise NotFoundException(f"Workflow '{request.workflow_code}' not found")
        return self._wf.create_instance(
            tenant_id=request.tenant_id,
            workflow_id=definition_id,
            entity_name=request.entity_name,
            entity_id=request.entity_id,
            started_by=request.started_by,
        )

    def approve(self, request: WorkflowActionRequest):
        return self._wf.approve(
            tenant_id=request.tenant_id,
            instance_id=request.instance_id,
            performed_by=request.performed_by,
            comments=request.comments,
        )

    def reject(self, request: WorkflowActionRequest):
        return self._wf.reject(
            tenant_id=request.tenant_id,
            instance_id=request.instance_id,
            performed_by=request.performed_by,
            comments=request.comments,
        )

    def cancel(self, request: WorkflowActionRequest):
        instance = self._wf.get_instance(request.tenant_id, request.instance_id)
        if instance.status in {
            WorkflowStatus.APPROVED,
            WorkflowStatus.REJECTED,
            WorkflowStatus.CANCELLED,
        }:
            raise WorkflowStateException("Workflow already completed")
        instance.status = WorkflowStatus.CANCELLED
        self._db.flush()
        self._audit.log_entity_change(
            tenant_id=request.tenant_id,
            entity_name="wf_instance",
            entity_id=request.instance_id,
            operation="cancel",
            performed_by=request.performed_by,
            new_value={"status": WorkflowStatus.CANCELLED.value, "comments": request.comments},
        )
        return instance
