"""Tenant router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.schemas import TenantCreateRequest, TenantResponse, TenantUpdateRequest
from modules.foundation.service.tenant_service import TenantService
from shared.schemas import APIResponse

router = APIRouter(prefix="/tenants", tags=["Tenants"])


@router.get("", response_model=APIResponse[list[TenantResponse]])
def list_tenants(
    _: Annotated[TenantContext, Depends(require_permission("foundation.tenant:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list[TenantResponse]]:
    tenants = TenantService(db).list_tenants()
    return APIResponse(
        message="Tenants retrieved",
        data=[TenantResponse(**t.__dict__) for t in tenants],
    )


@router.post("", response_model=APIResponse[TenantResponse])
def create_tenant(
    body: TenantCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.tenant:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[TenantResponse]:
    tenant = TenantService(db).create_tenant(
        tenant_code=body.tenant_code,
        tenant_name=body.tenant_name,
        created_by=ctx.user_id,
    )
    db.commit()
    return APIResponse(message="Tenant created", data=TenantResponse(**tenant.__dict__))


@router.get("/{tenant_id}", response_model=APIResponse[TenantResponse])
def get_tenant(
    tenant_id: UUID,
    _: Annotated[TenantContext, Depends(require_permission("foundation.tenant:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[TenantResponse]:
    tenant = TenantService(db).get_tenant(tenant_id)
    return APIResponse(message="Tenant retrieved", data=TenantResponse(**tenant.__dict__))


@router.put("/{tenant_id}", response_model=APIResponse[TenantResponse])
def update_tenant(
    tenant_id: UUID,
    body: TenantUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.tenant:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[TenantResponse]:
    tenant = TenantService(db).update_tenant(
        tenant_id,
        updated_by=ctx.user_id,
        **body.model_dump(exclude_unset=True),
    )
    db.commit()
    return APIResponse(message="Tenant updated", data=TenantResponse(**tenant.__dict__))


@router.delete("/{tenant_id}", response_model=APIResponse[None])
def delete_tenant(
    tenant_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.tenant:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    TenantService(db).delete_tenant(tenant_id, deleted_by=ctx.user_id)
    db.commit()
    return APIResponse(message="Tenant deleted", data=None)
