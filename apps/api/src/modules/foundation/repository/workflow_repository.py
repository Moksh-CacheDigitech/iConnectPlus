"""Workflow repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.entities import WorkflowDefinitionEntity, WorkflowInstanceEntity
from modules.foundation.models.workflow import WfAction, WfDefinition, WfInstance, WfStep
from modules.foundation.repository.base import TenantScopedRepository, utcnow


class WorkflowRepository(TenantScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_definitions(self, tenant_id: UUID) -> list[WorkflowDefinitionEntity]:
        stmt = select(WfDefinition).where(WfDefinition.tenant_id == tenant_id)
        return [self._def_to_entity(r) for r in self.db.scalars(stmt).all()]

    def get_definition(
        self, tenant_id: UUID, definition_id: UUID
    ) -> WorkflowDefinitionEntity | None:
        stmt = select(WfDefinition).where(
            WfDefinition.id == definition_id,
            WfDefinition.tenant_id == tenant_id,
        )
        row = self.db.scalar(stmt)
        return self._def_to_entity(row) if row else None

    def get_definition_by_code(
        self, tenant_id: UUID, workflow_code: str
    ) -> WorkflowDefinitionEntity | None:
        stmt = select(WfDefinition).where(
            WfDefinition.tenant_id == tenant_id,
            WfDefinition.workflow_code == workflow_code,
            WfDefinition.is_active.is_(True),
        ).order_by(WfDefinition.version_no.desc())
        row = self.db.scalar(stmt)
        return self._def_to_entity(row) if row else None

    def create_definition(
        self,
        *,
        tenant_id: UUID,
        workflow_code: str,
        workflow_name: str,
        module: str,
        document_type: str,
        created_by: UUID | None = None,
    ) -> WorkflowDefinitionEntity:
        row = WfDefinition(
            id=uuid4(),
            tenant_id=tenant_id,
            workflow_code=workflow_code,
            workflow_name=workflow_name,
            module=module,
            document_type=document_type,
            version_no=1,
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(row)
        self.db.flush()
        return self._def_to_entity(row)

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
    ) -> WfStep:
        row = WfStep(
            id=uuid4(),
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            step_order=step_order,
            step_code=step_code,
            step_name=step_name,
            approver_type=approver_type,
            created_by=created_by,
            updated_by=created_by,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_steps(self, workflow_id: UUID) -> list[WfStep]:
        stmt = select(WfStep).where(WfStep.workflow_id == workflow_id).order_by(WfStep.step_order)
        return list(self.db.scalars(stmt).all())

    def create_instance(
        self,
        *,
        tenant_id: UUID,
        workflow_id: UUID,
        entity_name: str,
        entity_id: UUID,
        started_by: UUID,
        current_step_id: UUID | None,
    ) -> WorkflowInstanceEntity:
        row = WfInstance(
            id=uuid4(),
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            entity_name=entity_name,
            entity_id=entity_id,
            current_step_id=current_step_id,
            status="pending",
            started_at=utcnow(),
            started_by=started_by,
            created_by=started_by,
            updated_by=started_by,
        )
        self.db.add(row)
        self.db.flush()
        return self._inst_to_entity(row)

    def get_instance(self, tenant_id: UUID, instance_id: UUID) -> WfInstance | None:
        stmt = select(WfInstance).where(
            WfInstance.id == instance_id,
            WfInstance.tenant_id == tenant_id,
        )
        return self.db.scalar(stmt)

    def list_instances(self, tenant_id: UUID) -> list[WorkflowInstanceEntity]:
        stmt = select(WfInstance).where(WfInstance.tenant_id == tenant_id)
        return [self._inst_to_entity(r) for r in self.db.scalars(stmt).all()]

    def record_action(
        self,
        *,
        tenant_id: UUID,
        instance_id: UUID,
        step_id: UUID,
        action: str,
        performed_by: UUID,
        comments: str | None = None,
    ) -> None:
        row = WfAction(
            id=uuid4(),
            tenant_id=tenant_id,
            instance_id=instance_id,
            step_id=step_id,
            action=action,
            comments=comments,
            performed_by=performed_by,
            performed_at=utcnow(),
        )
        self.db.add(row)
        self.db.flush()

    @staticmethod
    def _def_to_entity(row: WfDefinition) -> WorkflowDefinitionEntity:
        return WorkflowDefinitionEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            workflow_code=row.workflow_code,
            workflow_name=row.workflow_name,
            module=row.module,
            document_type=row.document_type,
            version_no=row.version_no,
            is_active=row.is_active,
        )

    @staticmethod
    def _inst_to_entity(row: WfInstance) -> WorkflowInstanceEntity:
        return WorkflowInstanceEntity(
            id=row.id,
            tenant_id=row.tenant_id,
            workflow_id=row.workflow_id,
            entity_name=row.entity_name,
            entity_id=row.entity_id,
            status=row.status,
            started_at=row.started_at,
            started_by=row.started_by,
            current_step_id=row.current_step_id,
            company_id=row.company_id,
        )
