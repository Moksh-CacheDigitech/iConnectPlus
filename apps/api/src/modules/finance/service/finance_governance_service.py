"""Finance governance - workflow, audit, notifications."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.enums import WORKFLOW_CODES
from modules.foundation.domain.enums import WorkflowStatus
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.compat.audit_facade import PlatformAuditFacade
from modules.platform.helpers.workflow_gate import resolve_workflow_definition_id
from modules.platform.compat.notify_facade import PlatformNotifyFacade
from modules.foundation.service.workflow_service import WorkflowService


class FinanceGovernanceService:
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

    def approve(
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
            )
            self._notify(ctx, entity_name, entity_id, "approved")
        return instance

    def reject(
        self,
        ctx: TenantContext,
        *,
        instance_id: UUID,
        entity_name: str,
        entity_id: UUID,
        on_rejected,
    ):
        instance = self._workflow.reject(
            tenant_id=ctx.tenant_id,
            instance_id=instance_id,
            performed_by=ctx.user_id,
        )
        on_rejected()
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name=entity_name,
            entity_id=entity_id,
            operation="reject",
            performed_by=ctx.user_id,
        )
        return instance

    def _notify(
        self, ctx: TenantContext, entity_name: str, entity_id: UUID, event: str
    ) -> None:
        # Notification templates seeded in future sprint; audit is primary trail.
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name=entity_name,
            entity_id=entity_id,
            operation=f"notify_{event}",
            performed_by=ctx.user_id,
        )
