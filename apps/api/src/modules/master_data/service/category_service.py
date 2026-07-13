"""Product category service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.domain.enums import MasterEntityType
from modules.master_data.models.category import MasterProductCategory
from modules.master_data.repository.category_repository import CategoryRepository
from modules.master_data.service.code_generator_service import CodeGeneratorService
from modules.master_data.service.duplicate_checker_service import DuplicateCheckerService
from modules.master_data.service.master_scope_validator import MasterScopeValidator


class CategoryService:
    def __init__(self, db: Session) -> None:
        self._repo = CategoryRepository(db)
        self._audit = AuditService(db)
        self._codes = CodeGeneratorService(db)
        self._duplicates = DuplicateCheckerService(db)
        self._scope = MasterScopeValidator(db)

    def list_categories(self, ctx: TenantContext, *, company_id: UUID | None = None):
        if company_id:
            self._scope.validate_company_access(ctx, company_id)
        return self._repo.list_categories(ctx, company_id=company_id)

    def get_category(self, ctx: TenantContext, category_id: UUID):
        category = self._repo.get_by_id(ctx, category_id)
        if category is None:
            raise NotFoundException("Category not found")
        self._scope.validate_company_access(ctx, category.company_id)
        return category

    def create_category(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        category_code: str | None = None,
        category_name: str,
        parent_category_id: UUID | None = None,
        level: int = 1,
        path: str | None = None,
    ):
        resolved_company_id = self._scope.resolve_company_id(ctx, company_id)

        if parent_category_id:
            parent = self._repo.get_by_id(ctx, parent_category_id)
            if parent is None:
                raise NotFoundException("Parent category not found")

        if category_code is None:
            category_code = self._codes.generate(
                MasterEntityType.PRODUCT_CATEGORY,
                resolved_company_id,
                model=MasterProductCategory,
                code_column="category_code",
            )
        else:
            self._duplicates.ensure_unique_code(
                model=MasterProductCategory,
                company_id=resolved_company_id,
                code=category_code,
                code_field="category_code",
                label="Category",
            )

        category = self._repo.create(
            ctx,
            company_id=resolved_company_id,
            category_code=category_code,
            category_name=category_name,
            parent_category_id=parent_category_id,
            level=level,
            path=path,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_product_category",
            entity_id=category.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={"category_code": category_code},
        )
        return category

    def update_category(self, ctx: TenantContext, category_id: UUID, **fields):
        self.get_category(ctx, category_id)
        updated = self._repo.update(ctx, category_id, **fields)
        if updated is None:
            raise NotFoundException("Category not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_product_category",
            entity_id=category_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def delete_category(self, ctx: TenantContext, category_id: UUID) -> None:
        self.get_category(ctx, category_id)
        if not self._repo.soft_delete(ctx, category_id):
            raise NotFoundException("Category not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_product_category",
            entity_id=category_id,
            operation="delete",
            performed_by=ctx.user_id,
        )
