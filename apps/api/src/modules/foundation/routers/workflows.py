"""Workflow router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.schemas import (
    WorkflowActionRequest,
    WorkflowDefinitionCreateRequest,
    WorkflowInstanceCreateRequest,
    WorkflowStepCreateRequest,
)
from modules.foundation.service.workflow_service import WorkflowService
from shared.schemas import APIResponse

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("/definitions", response_model=APIResponse[list])
def list_definitions(
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.workflow:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list]:
    definitions = WorkflowService(db).list_definitions(ctx.tenant_id)
    return APIResponse(message="Definitions retrieved", data=[d.__dict__ for d in definitions])


@router.post("/definitions", response_model=APIResponse[dict])
def create_definition(
    body: WorkflowDefinitionCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.workflow:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    definition = WorkflowService(db).create_definition(
        tenant_id=ctx.tenant_id,
        workflow_code=body.workflow_code,
        workflow_name=body.workflow_name,
        module=body.module,
        document_type=body.document_type,
        created_by=ctx.user_id,
    )
    db.commit()
    return APIResponse(message="Definition created", data=definition.__dict__)


@router.post("/definitions/{definition_id}/steps", response_model=APIResponse[dict])
def add_step(
    definition_id: UUID,
    body: WorkflowStepCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.workflow:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    step = WorkflowService(db).add_step(
        tenant_id=ctx.tenant_id,
        workflow_id=definition_id,
        step_order=body.step_order,
        step_code=body.step_code,
        step_name=body.step_name,
        approver_type=body.approver_type,
        created_by=ctx.user_id,
    )
    db.commit()
    return APIResponse(message="Step added", data={"id": str(step.id), "step_code": step.step_code})


@router.get("/instances", response_model=APIResponse[list])
def list_instances(
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.workflow:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list]:
    instances = WorkflowService(db).list_instances(ctx.tenant_id)
    return APIResponse(message="Instances retrieved", data=[i.__dict__ for i in instances])


@router.post("/instances", response_model=APIResponse[dict])
def create_instance(
    body: WorkflowInstanceCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.workflow:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = WorkflowService(db).create_instance(
        tenant_id=ctx.tenant_id,
        workflow_id=body.workflow_id,
        entity_name=body.entity_name,
        entity_id=body.entity_id,
        started_by=ctx.user_id,
    )
    db.commit()
    return APIResponse(message="Instance created", data=instance.__dict__)


@router.post("/instances/{instance_id}/approve", response_model=APIResponse[dict])
def approve_instance(
    instance_id: UUID,
    body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.workflow:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = WorkflowService(db).approve(
        tenant_id=ctx.tenant_id,
        instance_id=instance_id,
        performed_by=ctx.user_id,
        comments=body.comments,
    )
    db.commit()
    return APIResponse(
        message="Instance approved",
        data={"id": str(instance.id), "status": instance.status},
    )


@router.post("/instances/{instance_id}/reject", response_model=APIResponse[dict])
def reject_instance(
    instance_id: UUID,
    body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.workflow:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = WorkflowService(db).reject(
        tenant_id=ctx.tenant_id,
        instance_id=instance_id,
        performed_by=ctx.user_id,
        comments=body.comments,
    )
    db.commit()
    return APIResponse(
        message="Instance rejected",
        data={"id": str(instance.id), "status": instance.status},
    )
