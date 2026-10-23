"""ERP-admin module access: grant a user Admin or User on one module.

Admin grants go through UserService.set_user_modules and member grants through
ModuleAdminService, so Organization → Users and every module Users tab stay on the
same sec_user_module rows and side effects.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import AppException, ConflictException, NotFoundException
from modules.foundation.domain.entities import UserEntity
from modules.foundation.domain.erp_modules import (
    ERP_MODULE_KEY_SET,
    MODULE_ROLE_ADMIN,
    MODULE_ROLE_MEMBER,
)
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.repository.user_module_repository import UserModuleRepository
from modules.foundation.service.module_admin_service import ModuleAdminService
from modules.foundation.service.user_service import UserService


class ModuleAccessService:
    def __init__(self, db: Session) -> None:
        self._users = UserService(db)
        self._members = ModuleAdminService(db)
        self._modules = UserModuleRepository(db)

    @staticmethod
    def _require_module(module_key: str) -> str:
        key = (module_key or "").strip()
        if key not in ERP_MODULE_KEY_SET:
            raise AppException(f"Unknown module key: {module_key}")
        return key

    def _set_admin(self, ctx: TenantContext, user: UserEntity, module_key: str, *, grant: bool) -> None:
        keys = set(user.admin_module_keys)
        if grant:
            keys.add(module_key)
        else:
            keys.discard(module_key)
        self._users.set_user_modules(
            tenant_id=ctx.tenant_id,
            user_id=user.id,
            module_keys=sorted(keys),
            updated_by=ctx.user_id,
        )

    def grant(
        self,
        ctx: TenantContext,
        user_id: UUID,
        *,
        module_key: str,
        role: str,
        service_job_role: str | None = None,
    ) -> UserEntity:
        self._users.require_erp_admin(ctx.tenant_id, ctx.user_id)
        key = self._require_module(module_key)
        user = self._users.get_user(ctx.tenant_id, user_id)
        existing = self._modules.get_assignment(ctx.tenant_id, user_id, key)
        current = (existing.role or MODULE_ROLE_MEMBER) if existing else None

        if role == MODULE_ROLE_ADMIN:
            if current == MODULE_ROLE_ADMIN:
                raise ConflictException("User is already an admin of this module")
            self._set_admin(ctx, user, key, grant=True)
        elif role == MODULE_ROLE_MEMBER:
            if current is not None and current != MODULE_ROLE_ADMIN:
                raise ConflictException("User is already a user of this module")
            if current == MODULE_ROLE_ADMIN:
                self._set_admin(ctx, user, key, grant=False)
            self._members.add_member(ctx, key, user_id, service_job_role)
        else:
            raise AppException("role must be admin or member")
        return self._users.get_user(ctx.tenant_id, user_id)

    def revoke(self, ctx: TenantContext, user_id: UUID, *, module_key: str) -> UserEntity:
        self._users.require_erp_admin(ctx.tenant_id, ctx.user_id)
        key = self._require_module(module_key)
        user = self._users.get_user(ctx.tenant_id, user_id)
        existing = self._modules.get_assignment(ctx.tenant_id, user_id, key)
        if existing is None:
            raise NotFoundException("User has no access to this module")
        if (existing.role or MODULE_ROLE_MEMBER) == MODULE_ROLE_ADMIN:
            self._set_admin(ctx, user, key, grant=False)
        else:
            self._members.remove_member(ctx, key, user_id)
        return self._users.get_user(ctx.tenant_id, user_id)
