"""Master data governance and workflow orchestration."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.compat.audit_facade import PlatformAuditFacade
from modules.platform.helpers.workflow_gate import resolve_workflow_definition_id
from modules.platform.compat.notify_facade import PlatformNotifyFacade
from modules.foundation.service.workflow_service import WorkflowService
from modules.master_data.domain.enums import WORKFLOW_CODES


class GovernanceService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._workflow = WorkflowService(db)
        self._audit = PlatformAuditFacade(db)
        self._notifications = PlatformNotifyFacade(db)

    def submit_for_approval(
        self,
        ctx: TenantContext,
        *,
        entity_name: str,
        entity_id: UUID,
    ):
        definition_id = resolve_workflow_definition_id(
            self._db,
            tenant_id=ctx.tenant_id,
            entity_name=entity_name,
            module_workflow_code=WORKFLOW_CODES.get(entity_name),
            created_by=ctx.user_id,
        )
        instance = self._workflow.create_instance(
            tenant_id=ctx.tenant_id,
            workflow_id=definition_id,
            entity_name=entity_name,
            entity_id=entity_id,
            started_by=ctx.user_id,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name=entity_name,
            entity_id=entity_id,
            operation="submit",
            performed_by=ctx.user_id,
        )
        return instance

    def approve_and_activate(
        self,
        ctx: TenantContext,
        *,
        instance_id: UUID,
        entity_name: str,
        entity_id: UUID,
        on_approved,
    ):
        instance = self._workflow.approve(
            tenant_id=ctx.tenant_id,
            instance_id=instance_id,
            performed_by=ctx.user_id,
        )
        if instance.status == WorkflowStatus.APPROVED:
            on_approved()
            self._audit.log_entity_change(
                tenant_id=ctx.tenant_id,
                entity_name=entity_name,
                entity_id=entity_id,
                operation="approve",
                performed_by=ctx.user_id,
                new_value={"status": "active"},
            )
        return instance

    def reject(
        self,
        ctx: TenantContext,
        *,
        instance_id: UUID,
        entity_name: str,
        entity_id: UUID,
    ):
        instance = self._workflow.reject(
            tenant_id=ctx.tenant_id,
            instance_id=instance_id,
            performed_by=ctx.user_id,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name=entity_name,
            entity_id=entity_id,
            operation="reject",
            performed_by=ctx.user_id,
        )
        return instance

    def notify_created(
        self,
        ctx: TenantContext,
        *,
        event_type: str,
        entity_name: str,
        entity_id: UUID,
        payload: dict | None = None,
    ) -> None:
        templates = self._notifications.list_templates(ctx.tenant_id)
        template = next((t for t in templates if t.template_code == event_type), None)
        if template is None:
            return
        self._notifications.send(
            tenant_id=ctx.tenant_id,
            template_id=template.id,
            event_type=event_type,
            recipient_user_id=ctx.user_id,
            recipient_address=None,
            payload_json=payload or {"entity_name": entity_name, "entity_id": str(entity_id)},
            created_by=ctx.user_id,
        )
