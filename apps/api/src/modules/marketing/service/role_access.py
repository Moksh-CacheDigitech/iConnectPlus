"""Marketing team-role authorization helpers."""

from __future__ import annotations

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.erp_modules import (
    ADMIN_USER_TYPES,
    MARKETING_PLANNER_ROLES,
    MARKETING_ROLE_HEAD,
    MODULE_ROLE_ADMIN,
)
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.repository.user_module_repository import UserModuleRepository


def marketing_module_role(db: Session, ctx: TenantContext) -> str | None:
    if ctx.user_id is None:
        return None
    roles = UserModuleRepository(db).list_roles_for_user(ctx.tenant_id, ctx.user_id)
    return roles.get("marketing")


def is_marketing_module_admin(db: Session, ctx: TenantContext) -> bool:
    if ctx.user_type in ADMIN_USER_TYPES:
        return True
    if ctx.user_id is None:
        return False
    return UserModuleRepository(db).is_module_admin(ctx.tenant_id, ctx.user_id, "marketing")


def can_plan_marketing_work(db: Session, ctx: TenantContext) -> bool:
    """Vishakha (head) or Ansh (associate/content creator) can create events & deliverables."""
    if is_marketing_module_admin(db, ctx):
        return True
    role = marketing_module_role(db, ctx)
    if role == MODULE_ROLE_ADMIN:
        return True
    return role in MARKETING_PLANNER_ROLES


def ensure_can_create_campaign(db: Session, ctx: TenantContext) -> None:
    """Campaigns / events may be created by Marketing head or associate planners."""
    if can_plan_marketing_work(db, ctx):
        return
    raise ForbiddenException(
        "Only Marketing head or Marketing associate can create campaigns / events"
    )


def ensure_can_manage_deliverables(db: Session, ctx: TenantContext) -> None:
    """Deliverables and approval-head assignment: head or associate."""
    if can_plan_marketing_work(db, ctx):
        return
    raise ForbiddenException(
        "Only Marketing head or Marketing associate can add campaign deliverables"
    )


def is_marketing_head(db: Session, ctx: TenantContext) -> bool:
    if is_marketing_module_admin(db, ctx):
        return True
    return marketing_module_role(db, ctx) == MARKETING_ROLE_HEAD
