"""Role service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.foundation.repository.role_repository import PermissionRepository, RoleRepository
from modules.foundation.service.audit_service import AuditService
from modules.foundation.service.rbac_service import RBACService


class RoleService:
    def __init__(self, db: Session) -> None:
        self._repo = RoleRepository(db)
        self._permissions = PermissionRepository(db)
        self._audit = AuditService(db)
        self._rbac = RBACService(db)

    def list_roles(self, tenant_id: UUID):
        return self._repo.list_roles(tenant_id)

    def get_role(self, tenant_id: UUID, role_id: UUID):
        role = self._repo.get_by_id(tenant_id, role_id)
        if role is None:
            raise NotFoundException("Role not found")
        return role

    def create_role(
        self,
        *,
        tenant_id: UUID,
        role_code: str,
        role_name: str,
        description: str | None = None,
        created_by: UUID | None = None,
    ):
        if self._repo.get_by_code(tenant_id, role_code):
            raise ConflictException("Role code already exists")
        role = self._repo.create(
            tenant_id=tenant_id,
            role_code=role_code,
            role_name=role_name,
            description=description,
            created_by=created_by,
        )
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="sec_role",
            entity_id=role.id,
            operation="create",
            performed_by=created_by,
            new_value={"role_code": role_code},
        )
        return role

    def update_role(self, tenant_id: UUID, role_id: UUID, updated_by: UUID | None = None, **fields):
        role = self._repo.update(tenant_id, role_id, **fields)
        if role is None:
            raise NotFoundException("Role not found")
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="sec_role",
            entity_id=role_id,
            operation="update",
            performed_by=updated_by,
            new_value=fields,
        )
        return role

    def delete_role(self, tenant_id: UUID, role_id: UUID, deleted_by: UUID | None = None) -> None:
        role = self._repo.get_by_id(tenant_id, role_id)
        if role is None:
            raise NotFoundException("Role not found")
        if role.is_system_role:
            raise ConflictException("System roles cannot be deleted")
        if not self._repo.soft_delete(tenant_id, role_id, deleted_by=deleted_by):
            raise NotFoundException("Role not found")

    def grant_permission(
        self,
        *,
        tenant_id: UUID,
        role_id: UUID,
        permission_id: UUID,
        granted_by: UUID | None,
    ) -> None:
        if self._permissions.get_by_id(permission_id) is None:
            raise NotFoundException("Permission not found")
        self._repo.grant_permission(
            tenant_id=tenant_id,
            role_id=role_id,
            permission_id=permission_id,
            granted_by=granted_by,
        )
        self._audit.log_entity_change(
            tenant_id=tenant_id,
            entity_name="sec_role_permission",
            entity_id=role_id,
            operation="create",
            performed_by=granted_by,
            new_value={"permission_id": str(permission_id)},
        )

    def list_permissions(self, *, module: str | None = None):
        return self._permissions.list_all(module=module)

    def list_permission_modules(self):
        return self._permissions.list_modules()
