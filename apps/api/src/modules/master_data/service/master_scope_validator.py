"""Master data scope validation."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.org_data_scope import (
    resolve_list_company_id as shared_resolve_list_company_id,
    resolve_write_company_id as shared_resolve_write_company_id,
)
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.service.org_scope_validator import OrgScopeValidator

MASTER_DATA_MODULE_KEY = "master-data"


class MasterScopeValidator:
    def __init__(self, db: Session) -> None:
        self._org_scope = OrgScopeValidator(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self._org_scope.validate_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self._org_scope.validate_branch_access(ctx, branch_id)

    def resolve_list_company_id(
        self, ctx: TenantContext, company_id: UUID | None
    ) -> UUID | None:
        if company_id is not None:
            self.validate_company_access(ctx, company_id)
        return shared_resolve_list_company_id(
            ctx, company_id, module_key=MASTER_DATA_MODULE_KEY
        )

    def resolve_company_id(self, ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            self.validate_company_access(ctx, company_id)
            return company_id
        return shared_resolve_write_company_id(ctx, None)
