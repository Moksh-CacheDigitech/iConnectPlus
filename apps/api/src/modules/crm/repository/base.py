"""CRM repository base utilities."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.org_data_scope import (
    apply_org_scope_filter,
    resolve_list_company_id as shared_resolve_list_company_id,
    resolve_write_company_id as shared_resolve_write_company_id,
)
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository

CRM_MODULE_KEY = "crm"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CrmScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_crm_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        # CRM isolates non-admins via creator/visibility rules, not session branch.
        # Branch-scoping here caused "Branch scope mismatch" and empty lists whenever
        # a company/lead lived on another branch of the same company.
        _ = branch_scoped
        stmt = CrmScopedRepository.apply_tenant_filter(stmt, model, ctx)
        return apply_org_scope_filter(
            stmt, model, ctx, module_key=CRM_MODULE_KEY, branch_scoped=False
        )

    @staticmethod
    def resolve_list_company_id(
        ctx: TenantContext, company_id: UUID | None
    ) -> UUID | None:
        """Optional company filter for list/read APIs (never session-pin alone)."""
        if company_id is not None:
            CrmScopedRepository.ensure_company_access(
                ctx, company_id, module_key=CRM_MODULE_KEY
            )
        return shared_resolve_list_company_id(
            ctx, company_id, module_key=CRM_MODULE_KEY
        )

    @staticmethod
    def resolve_company_id(ctx: TenantContext, company_id: UUID | None) -> UUID:
        """Concrete company for create/update - always requires a single company."""
        if company_id is not None:
            CrmScopedRepository.ensure_company_access(
                ctx, company_id, module_key=CRM_MODULE_KEY
            )
            return company_id
        return shared_resolve_write_company_id(ctx, None)
