"""Procurement scope validation."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException, NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.branch_repository import BranchRepository
from modules.organization.repository.company_repository import CompanyRepository


class ProcurementScopeValidator:
    def __init__(self, db: Session) -> None:
        self._company_repo = CompanyRepository(db)
        self._branch_repo = BranchRepository(db)

    def resolve_company_id(self, ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            self.validate_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        if ctx.user_type in {"super_admin", "tenant_admin"}:
            return
        if ctx.company_id and ctx.company_id != company_id:
            raise ForbiddenException("Company scope mismatch")
        company = self._company_repo.get_by_id(ctx, company_id)
        if company is None:
            raise NotFoundException("Company not found")

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        if ctx.user_type in {"super_admin", "tenant_admin"}:
            return
        if ctx.branch_id and ctx.branch_id != branch_id:
            raise ForbiddenException("Branch scope mismatch")
