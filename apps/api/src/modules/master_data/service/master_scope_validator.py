"""Master data scope validation."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.service.org_scope_validator import OrgScopeValidator


class MasterScopeValidator:
    def __init__(self, db: Session) -> None:
        self._org_scope = OrgScopeValidator(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self._org_scope.validate_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self._org_scope.validate_branch_access(ctx, branch_id)

    def resolve_company_id(self, ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            self.validate_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
