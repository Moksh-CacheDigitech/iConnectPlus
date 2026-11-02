"""Procurement scope validation."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException, NotFoundException
from modules.foundation.domain.org_data_scope import (
    effective_company_ids,
    has_module_wide_data_access,
    is_platform_admin,
    resolve_list_company_id as shared_resolve_list_company_id,
    resolve_write_company_id as shared_resolve_write_company_id,
)
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository
from modules.organization.repository.branch_repository import BranchRepository
from modules.organization.repository.company_repository import CompanyRepository

PROCUREMENT_MODULE_KEY = "procurement"


class ProcurementScopeValidator:
    def __init__(self, db: Session) -> None:
        self._company_repo = CompanyRepository(db)
        self._branch_repo = BranchRepository(db)

    def resolve_list_company_id(
        self, ctx: TenantContext, company_id: UUID | None
    ) -> UUID | None:
        """Optional company filter for list/read APIs (never session-pin alone)."""
        if company_id is not None:
            self.validate_company_access(ctx, company_id)
        return shared_resolve_list_company_id(
            ctx, company_id, module_key=PROCUREMENT_MODULE_KEY
        )

    def resolve_company_id(self, ctx: TenantContext, company_id: UUID | None) -> UUID:
        """Concrete company for create/update - always requires a single company."""
        if company_id is not None:
            self.validate_company_access(ctx, company_id)
            return company_id
        return shared_resolve_write_company_id(ctx, None)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        OrgScopedRepository.ensure_company_access(
            ctx, company_id, module_key=PROCUREMENT_MODULE_KEY
        )
        company = self._company_repo.get_by_id(ctx, company_id)
        if company is None:
            raise NotFoundException("Company not found")

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        """Allow any branch under companies the user can access.

        Session branch must not block SCM Create PO / approval on an OVF from
        another company or branch (e.g. CT OVF while parked on CDPL HQ).
        """
        if has_module_wide_data_access(ctx, PROCUREMENT_MODULE_KEY) or is_platform_admin(ctx):
            return

        allowed = effective_company_ids(ctx, module_key=PROCUREMENT_MODULE_KEY)
        if allowed is None:
            return
        if not allowed:
            raise ForbiddenException("Branch scope mismatch")

        branch = self._branch_repo.get_by_id(ctx, branch_id)
        company_id = getattr(branch, "company_id", None) if branch is not None else None
        if company_id is not None and company_id in allowed:
            return

        if ctx.branch_id and ctx.branch_id == branch_id:
            return

        raise ForbiddenException("Branch scope mismatch")
