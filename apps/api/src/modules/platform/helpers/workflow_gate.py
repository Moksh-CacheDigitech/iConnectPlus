"""Resolve / provision workflow definitions from the APPROVAL_POLICIES matrix."""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.repository.setting_repository import SettingRepository
from modules.foundation.repository.workflow_repository import WorkflowRepository
from modules.foundation.service.workflow_service import WorkflowService
from modules.platform.policies import (
    WORKFLOW_CODE_SETTING_PREFIX,
    ApprovalMode,
    approval_policy,
    policy_for_entity,
)

logger = logging.getLogger(__name__)


def _tenant_override(db: Session, tenant_id: UUID, entity_name: str) -> str | None:
    setting = SettingRepository(db).get_by_key(tenant_id, f"{WORKFLOW_CODE_SETTING_PREFIX}{entity_name}")
    if setting is None or not setting.setting_value:
        return None
    return str(setting.setting_value).strip() or None


def resolve_workflow_definition_id(
    db: Session,
    *,
    tenant_id: UUID,
    entity_name: str,
    module_workflow_code: str | None,
    created_by: UUID | None,
) -> UUID:
    """Definition id for an entity: tenant override → module code → policy matrix.

    Provisions a single-step default definition when the policy is workflow-backed
    and the tenant has none yet. Raises NotFoundException when no policy applies.
    """
    policy = policy_for_entity(entity_name)
    workflow_code = (
        _tenant_override(db, tenant_id, entity_name)
        or module_workflow_code
        or (policy.workflow_code if policy else None)
    )
    if workflow_code is None:
        raise NotFoundException("No workflow configured for this entity")

    repo = WorkflowRepository(db)
    definition = repo.get_definition_by_code(tenant_id, workflow_code)
    if definition is not None:
        return definition.id

    if policy is None or policy.mode != ApprovalMode.WORKFLOW:
        raise NotFoundException("Workflow definition not found")

    service = WorkflowService(db)
    created = service.create_definition(
        tenant_id=tenant_id,
        workflow_code=workflow_code,
        workflow_name=f"{policy.module.replace('_', ' ').title()} {policy.document_type.replace('_', ' ')} approval",
        module=policy.module,
        document_type=entity_name,
        created_by=created_by,
    )
    service.add_step(
        tenant_id=tenant_id,
        workflow_id=created.id,
        step_order=1,
        step_code=policy.approver_role,
        step_name=f"{policy.approver_role.replace('_', ' ').title()} approval",
        approver_type="role",
        created_by=created_by,
    )
    logger.info(
        "workflow.default_provisioned",
        extra={"tenant_id": str(tenant_id), "workflow_code": workflow_code, "entity": entity_name},
    )
    return created.id


def start_approval_if_required(
    db: Session,
    *,
    document_key: str,
    tenant_id: UUID,
    entity_name: str,
    entity_id: UUID,
    started_by: UUID,
) -> UUID | None:
    """Start a workflow for a matrix document key; None when the policy is not workflow-backed."""
    policy = approval_policy(document_key)
    if policy is None or policy.mode != ApprovalMode.WORKFLOW:
        return None
    definition_id = resolve_workflow_definition_id(
        db,
        tenant_id=tenant_id,
        entity_name=policy.entity_name or entity_name,
        module_workflow_code=policy.workflow_code,
        created_by=started_by,
    )
    instance = WorkflowService(db).create_instance(
        tenant_id=tenant_id,
        workflow_id=definition_id,
        entity_name=entity_name,
        entity_id=entity_id,
        started_by=started_by,
    )
    return instance.id
