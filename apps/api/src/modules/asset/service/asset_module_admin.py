"""Assets module admin - ERP admins (DB user_type), org-assigned module admins, or asset RBAC admin."""

from __future__ import annotations

from sqlalchemy.orm import Session

from modules.foundation.domain.erp_modules import ADMIN_USER_TYPES
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.repository.user_module_repository import UserModuleRepository
from modules.foundation.service.rbac_service import RBACService

ASSET_MODULE_KEY = "assets"
ASSET_MANAGER_ROLE_CODE = "ASSET_MANAGER"


class AssetModuleAdminService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._modules = UserModuleRepository(db)
        self._rbac = RBACService(db)

    def is_admin(self, ctx: TenantContext) -> bool:
        if ctx.user_id is None:
            return False
        if ctx.user_type in ADMIN_USER_TYPES:
            return True
        if ASSET_MODULE_KEY in ctx.admin_module_keys:
            return True
        if self._modules.is_module_admin(ctx.tenant_id, ctx.user_id, ASSET_MODULE_KEY):
            return True
        return self._rbac.has_permission(ctx.user_id, ctx.tenant_id, "asset.module:admin")

    def ensure_admin(self, ctx: TenantContext) -> None:
        from core.exceptions import ForbiddenException

        if not self.is_admin(ctx):
            raise ForbiddenException("Assets module admin access required")
