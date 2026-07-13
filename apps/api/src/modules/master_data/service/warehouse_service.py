"""Warehouse service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.domain.enums import MasterEntityType
from modules.master_data.models.warehouse import MasterWarehouse
from modules.master_data.repository.warehouse_repository import WarehouseRepository
from modules.master_data.service.code_generator_service import CodeGeneratorService
from modules.master_data.service.duplicate_checker_service import DuplicateCheckerService
from modules.master_data.service.master_scope_validator import MasterScopeValidator


class WarehouseService:
    def __init__(self, db: Session) -> None:
        self._repo = WarehouseRepository(db)
        self._audit = AuditService(db)
        self._codes = CodeGeneratorService(db)
        self._duplicates = DuplicateCheckerService(db)
        self._scope = MasterScopeValidator(db)

    def list_warehouses(
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
        return self._repo.list_warehouses(ctx, company_id=company_id, branch_id=branch_id)

    def get_warehouse(self, ctx: TenantContext, warehouse_id: UUID):
        warehouse = self._repo.get_by_id(ctx, warehouse_id)
        if warehouse is None:
            raise NotFoundException("Warehouse not found")
        self._scope.validate_company_access(ctx, warehouse.company_id)
        self._scope.validate_branch_access(ctx, warehouse.branch_id)
        return warehouse

    def create_warehouse(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        branch_id: UUID,
        warehouse_code: str | None = None,
        warehouse_name: str,
        warehouse_type: str,
        location_id: UUID | None = None,
        is_default: bool = False,
        address_json: dict | None = None,
    ):
        resolved_company_id = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)

        if warehouse_code is None:
            warehouse_code = self._codes.generate(
                MasterEntityType.WAREHOUSE,
                resolved_company_id,
                model=MasterWarehouse,
                code_column="warehouse_code",
            )
        else:
            self._duplicates.ensure_unique_code(
                model=MasterWarehouse,
                company_id=resolved_company_id,
                code=warehouse_code,
                code_field="warehouse_code",
                label="Warehouse",
            )

        warehouse = self._repo.create(
            ctx,
            company_id=resolved_company_id,
            branch_id=branch_id,
            warehouse_code=warehouse_code,
            warehouse_name=warehouse_name,
            warehouse_type=warehouse_type,
            location_id=location_id,
            is_default=is_default,
            address_json=address_json,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_warehouse",
            entity_id=warehouse.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={"warehouse_code": warehouse_code, "branch_id": str(branch_id)},
        )
        return warehouse

    def update_warehouse(self, ctx: TenantContext, warehouse_id: UUID, **fields):
        self.get_warehouse(ctx, warehouse_id)
        if "branch_id" in fields and fields["branch_id"] is not None:
            self._scope.validate_branch_access(ctx, fields["branch_id"])

        updated = self._repo.update(ctx, warehouse_id, **fields)
        if updated is None:
            raise NotFoundException("Warehouse not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_warehouse",
            entity_id=warehouse_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def delete_warehouse(self, ctx: TenantContext, warehouse_id: UUID) -> None:
        self.get_warehouse(ctx, warehouse_id)
        if not self._repo.soft_delete(ctx, warehouse_id):
            raise NotFoundException("Warehouse not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_warehouse",
            entity_id=warehouse_id,
            operation="delete",
            performed_by=ctx.user_id,
        )
