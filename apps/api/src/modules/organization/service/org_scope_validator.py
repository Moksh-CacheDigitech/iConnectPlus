"""Organization scope validation service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.org_scope_repository import OrgScopeRepository


class OrgScopeValidator:
    def __init__(self, db: Session) -> None:
        self._repo = OrgScopeRepository(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        if not self._repo.user_has_company_access(ctx, company_id):
            raise ForbiddenException("No access to this company")

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        if not self._repo.user_has_branch_access(ctx, branch_id):
            raise ForbiddenException("No access to this branch")
