"""Role and permission routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.schemas import (
    GrantPermissionRequest,
    PermissionResponse,
    RoleCreateRequest,
    RoleResponse,
    RoleUpdateRequest,
)
from modules.foundation.service.role_service import RoleService
from shared.schemas import APIResponse

roles_router = APIRouter(prefix="/roles", tags=["Roles"])
permissions_router = APIRouter(prefix="/permissions", tags=["Permissions"])


@roles_router.get("", response_model=APIResponse[list[RoleResponse]])
def list_roles(
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.role:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list[RoleResponse]]:
    roles = RoleService(db).list_roles(ctx.tenant_id)
    return APIResponse(message="Roles retrieved", data=[RoleResponse(**r.__dict__) for r in roles])


@roles_router.post("", response_model=APIResponse[RoleResponse])
def create_role(
    body: RoleCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.role:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RoleResponse]:
    role = RoleService(db).create_role(
        tenant_id=ctx.tenant_id,
        role_code=body.role_code,
        role_name=body.role_name,
        description=body.description,
        created_by=ctx.user_id,
    )
    db.commit()
    return APIResponse(message="Role created", data=RoleResponse(**role.__dict__))


@roles_router.get("/{role_id}", response_model=APIResponse[RoleResponse])
def get_role(
    role_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.role:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RoleResponse]:
    role = RoleService(db).get_role(ctx.tenant_id, role_id)
    return APIResponse(message="Role retrieved", data=RoleResponse(**role.__dict__))


@roles_router.put("/{role_id}", response_model=APIResponse[RoleResponse])
def update_role(
    role_id: UUID,
    body: RoleUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.role:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RoleResponse]:
    role = RoleService(db).update_role(
        ctx.tenant_id,
        role_id,
        updated_by=ctx.user_id,
        **body.model_dump(exclude_unset=True),
    )
    db.commit()
    return APIResponse(message="Role updated", data=RoleResponse(**role.__dict__))


@roles_router.delete("/{role_id}", response_model=APIResponse[None])
def delete_role(
    role_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.role:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    RoleService(db).delete_role(ctx.tenant_id, role_id, deleted_by=ctx.user_id)
    db.commit()
    return APIResponse(message="Role deleted", data=None)


@roles_router.post("/{role_id}/permissions", response_model=APIResponse[None])
def grant_permission(
    role_id: UUID,
    body: GrantPermissionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.role:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    RoleService(db).grant_permission(
        tenant_id=ctx.tenant_id,
        role_id=role_id,
        permission_id=body.permission_id,
        granted_by=ctx.user_id,
    )
    db.commit()
    return APIResponse(message="Permission granted", data=None)


@permissions_router.get("", response_model=APIResponse[list[PermissionResponse]])
def list_permissions(
    _: Annotated[TenantContext, Depends(require_permission("foundation.permission:read"))],
    db: Annotated[Session, Depends(get_db)],
    module: str | None = None,
) -> APIResponse[list[PermissionResponse]]:
    permissions = RoleService(db).list_permissions(module=module)
    return APIResponse(
        message="Permissions retrieved",
        data=[PermissionResponse(**p.__dict__) for p in permissions],
    )


@permissions_router.get("/modules", response_model=APIResponse[list[str]])
def list_modules(
    _: Annotated[TenantContext, Depends(require_permission("foundation.permission:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list[str]]:
    modules = RoleService(db).list_permission_modules()
    return APIResponse(message="Modules retrieved", data=modules)


@permissions_router.get("/{permission_id}", response_model=APIResponse[PermissionResponse])
def get_permission(
    permission_id: UUID,
    _: Annotated[TenantContext, Depends(require_permission("foundation.permission:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PermissionResponse]:
    from modules.foundation.repository.role_repository import PermissionRepository

    permission = PermissionRepository(db).get_by_id(permission_id)
    if permission is None:
        from core.exceptions import NotFoundException

        raise NotFoundException("Permission not found")
    return APIResponse(
        message="Permission retrieved",
        data=PermissionResponse(**permission.__dict__),
    )
