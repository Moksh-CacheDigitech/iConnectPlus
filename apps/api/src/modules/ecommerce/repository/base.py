"""Ecommerce repository base utilities."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.org_data_scope import (
    apply_org_scope_filter,
    resolve_list_company_id as shared_resolve_list_company_id,
    resolve_write_company_id as shared_resolve_write_company_id,
)
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository

MODULE_KEY = "ecommerce"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EcommerceScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_ecommerce_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = EcommerceScopedRepository.apply_tenant_filter(stmt, model, ctx)
        return apply_org_scope_filter(
            stmt, model, ctx, module_key=MODULE_KEY, branch_scoped=branch_scoped
        )

    @staticmethod
    def resolve_list_company_id(
        ctx: TenantContext, company_id: UUID | None
    ) -> UUID | None:
        """Optional company filter for list/read APIs (never session-pin alone)."""
        if company_id is not None:
            EcommerceScopedRepository.ensure_company_access(
                ctx, company_id, module_key=MODULE_KEY
            )
        return shared_resolve_list_company_id(
            ctx, company_id, module_key=MODULE_KEY
        )

    @staticmethod
    def resolve_company_id(ctx: TenantContext, company_id: UUID | None) -> UUID:
        """Concrete company for create/update - always requires a single company."""
        if company_id is not None:
            EcommerceScopedRepository.ensure_company_access(
                ctx, company_id, module_key=MODULE_KEY
            )
            return company_id
        return shared_resolve_write_company_id(ctx, None)
