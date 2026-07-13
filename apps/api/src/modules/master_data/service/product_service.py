"""Product service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import AppException, NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.domain.enums import MasterEntityType
from modules.master_data.models.product import MasterProduct
from modules.master_data.repository.product_repository import ProductRepository
from modules.master_data.repository.uom_repository import UomRepository
from modules.master_data.service.code_generator_service import CodeGeneratorService
from modules.master_data.service.duplicate_checker_service import DuplicateCheckerService
from modules.master_data.service.governance_service import GovernanceService
from modules.master_data.service.master_scope_validator import MasterScopeValidator


class ProductService:
    def __init__(self, db: Session) -> None:
        self._repo = ProductRepository(db)
        self._uoms = UomRepository(db)
        self._audit = AuditService(db)
        self._codes = CodeGeneratorService(db)
        self._duplicates = DuplicateCheckerService(db)
        self._scope = MasterScopeValidator(db)
        self._governance = GovernanceService(db)

    def list_products(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID | None = None,
    ):
        if company_id:
            self._scope.validate_company_access(ctx, company_id)
        if branch_id:
            self._scope.validate_branch_access(ctx, branch_id)
        return self._repo.list_products(ctx, company_id=company_id, branch_id=branch_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        product = self._repo.get_by_id(ctx, product_id)
        if product is None:
            raise NotFoundException("Product not found")
        self._scope.validate_company_access(ctx, product.company_id)
        return product

    def create_product(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        product_code: str | None = None,
        product_name: str,
        product_type: str,
        uom_id: UUID,
        branch_id: UUID | None = None,
        category_id: UUID | None = None,
        tax_id: UUID | None = None,
        barcode: str | None = None,
        is_inventory_tracked: bool = True,
    ):
        if uom_id is None:
            raise AppException("uom_id is required")

        resolved_company_id = self._scope.resolve_company_id(ctx, company_id)
        if branch_id:
            self._scope.validate_branch_access(ctx, branch_id)
        if self._uoms.get_by_id(ctx, uom_id) is None:
            raise NotFoundException("UOM not found")

        if product_code is None:
            product_code = self._codes.generate(
                MasterEntityType.PRODUCT,
                resolved_company_id,
                model=MasterProduct,
                code_column="product_code",
            )
        else:
            self._duplicates.ensure_unique_code(
                model=MasterProduct,
                company_id=resolved_company_id,
                code=product_code,
                code_field="product_code",
                label="Product",
            )

        product = self._repo.create(
            ctx,
            company_id=resolved_company_id,
            product_code=product_code,
            product_name=product_name,
            product_type=product_type,
            uom_id=uom_id,
            branch_id=branch_id,
            category_id=category_id,
            tax_id=tax_id,
            barcode=barcode,
            is_inventory_tracked=is_inventory_tracked,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_product",
            entity_id=product.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={"product_code": product_code, "uom_id": str(uom_id)},
        )
        return product

    def update_product(self, ctx: TenantContext, product_id: UUID, **fields):
        self.get_product(ctx, product_id)
        if "uom_id" in fields:
            if fields["uom_id"] is None:
                raise AppException("uom_id is required")
            if self._uoms.get_by_id(ctx, fields["uom_id"]) is None:
                raise NotFoundException("UOM not found")
        if "branch_id" in fields and fields["branch_id"] is not None:
            self._scope.validate_branch_access(ctx, fields["branch_id"])

        updated = self._repo.update(ctx, product_id, **fields)
        if updated is None:
            raise NotFoundException("Product not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_product",
            entity_id=product_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def delete_product(self, ctx: TenantContext, product_id: UUID) -> None:
        self.get_product(ctx, product_id)
        if not self._repo.soft_delete(ctx, product_id):
            raise NotFoundException("Product not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_product",
            entity_id=product_id,
            operation="delete",
            performed_by=ctx.user_id,
        )

    def submit_for_approval(self, ctx: TenantContext, product_id: UUID):
        self.get_product(ctx, product_id)
        return self._governance.submit_for_approval(
            ctx,
            entity_name="master_product",
            entity_id=product_id,
        )
