"""Workflow service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.exceptions import WorkflowStateException
from modules.foundation.repository.workflow_repository import WorkflowRepository
from modules.foundation.service.audit_service import AuditService


class WorkflowService:
    def __init__(self, db: Session) -> None:
        self._repo = WorkflowRepository(db)
        self._audit = AuditService(db)

    def list_definitions(self, tenant_id: UUID):
        return self._repo.list_definitions(tenant_id)

    def get_definition(self, tenant_id: UUID, definition_id: UUID):
        definition = self._repo.get_definition(tenant_id, definition_id)
        if definition is None:
            raise NotFoundException("Workflow definition not found")
        return definition

    def create_definition(
        self,
        *,
        tenant_id: UUID,
        workflow_code: str,
        workflow_name: str,
        module: str,
        document_type: str,
        created_by: UUID | None = None,
    ):
        definition = self._repo.create_definition(
            tenant_id=tenant_id,
            workflow_code=workflow_code,
            workflow_name=workflow_name,
            module=module,
            document_type=document_type,
            created_by=created_by,
        )
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="wf_definition",
            entity_id=definition.id,
            operation="create",
            performed_by=created_by,
            new_value={"workflow_code": workflow_code},
        )
        return definition

    def add_step(
        self,
        *,
        tenant_id: UUID,
        workflow_id: UUID,
        step_order: int,
        step_code: str,
        step_name: str,
        approver_type: str,
        created_by: UUID | None = None,
    ):
        if self._repo.get_definition(tenant_id, workflow_id) is None:
            raise NotFoundException("Workflow definition not found")
        return self._repo.add_step(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            step_order=step_order,
            step_code=step_code,
            step_name=step_name,
            approver_type=approver_type,
            created_by=created_by,
        )

    def create_instance(
        self,
        *,
        tenant_id: UUID,
        workflow_id: UUID,
        entity_name: str,
        entity_id: UUID,
        started_by: UUID,
    ):
        steps = self._repo.get_steps(workflow_id)
        first_step = steps[0].id if steps else None
        instance = self._repo.create_instance(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            entity_name=entity_name,
            entity_id=entity_id,
            started_by=started_by,
            current_step_id=first_step,
        )
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="wf_instance",
            entity_id=instance.id,
            operation="create",
            performed_by=started_by,
        )
        return instance

    def list_instances(self, tenant_id: UUID):
        return self._repo.list_instances(tenant_id)

    def get_instance(self, tenant_id: UUID, instance_id: UUID):
        instance = self._repo.get_instance(tenant_id, instance_id)
        if instance is None:
            raise NotFoundException("Workflow instance not found")
        return instance

    def approve(
        self,
        *,
        tenant_id: UUID,
        instance_id: UUID,
        performed_by: UUID,
        comments: str | None = None,
    ):
        return self._transition(
            tenant_id=tenant_id,
            instance_id=instance_id,
            action="approve",
            performed_by=performed_by,
            comments=comments,
            terminal_status=WorkflowStatus.APPROVED,
        )

    def reject(
        self,
        *,
        tenant_id: UUID,
        instance_id: UUID,
        performed_by: UUID,
        comments: str | None = None,
    ):
        return self._transition(
            tenant_id=tenant_id,
            instance_id=instance_id,
            action="reject",
            performed_by=performed_by,
            comments=comments,
            terminal_status=WorkflowStatus.REJECTED,
        )

    def _transition(
        self,
        *,
        tenant_id: UUID,
        instance_id: UUID,
        action: str,
        performed_by: UUID,
        comments: str | None,
        terminal_status: WorkflowStatus,
    ):
        instance = self._repo.get_instance(tenant_id, instance_id)
        if instance is None:
            raise NotFoundException("Workflow instance not found")
        if instance.status in {WorkflowStatus.APPROVED, WorkflowStatus.REJECTED}:
            raise WorkflowStateException("Workflow already completed")
        if instance.current_step_id is None:
            raise WorkflowStateException("No active workflow step")

        self._repo.record_action(
            tenant_id=tenant_id,
            instance_id=instance_id,
            step_id=instance.current_step_id,
            action=action,
            performed_by=performed_by,
            comments=comments,
        )

        steps = self._repo.get_steps(instance.workflow_id)
        current_index = next(
            (i for i, s in enumerate(steps) if s.id == instance.current_step_id),
            -1,
        )
        if action == "reject":
            instance.status = WorkflowStatus.REJECTED
        elif current_index + 1 < len(steps):
            instance.status = WorkflowStatus.IN_PROGRESS
            instance.current_step_id = steps[current_index + 1].id
        else:
            instance.status = WorkflowStatus.APPROVED

        self._db = self._repo.db
        self._repo.db.flush()
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="wf_instance",
            entity_id=instance_id,
            operation=action,
            performed_by=performed_by,
            new_value={"status": instance.status},
        )
        return instance
