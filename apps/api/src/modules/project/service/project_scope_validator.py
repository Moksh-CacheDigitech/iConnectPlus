"""Project scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.project.repository.base import PrjScopedRepository


class ProjectScopeValidator(PrjScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id, module_key="projects")

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id, module_key="projects")

    def resolve_list_company_id(
        self, ctx: TenantContext, company_id: UUID | None
    ) -> UUID | None:
        return PrjScopedRepository.resolve_list_company_id(ctx, company_id)
