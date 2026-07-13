"""UOM service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.models.reference import MasterUom
from modules.master_data.repository.uom_repository import UomRepository
from modules.master_data.service.duplicate_checker_service import DuplicateCheckerService
from modules.master_data.service.master_scope_validator import MasterScopeValidator


class UomService:
    def __init__(self, db: Session) -> None:
        self._repo = UomRepository(db)
        self._audit = AuditService(db)
        self._duplicates = DuplicateCheckerService(db)
        self._scope = MasterScopeValidator(db)

    def list_uoms(self, ctx: TenantContext, *, company_id: UUID | None = None):
        if company_id:
            self._scope.validate_company_access(ctx, company_id)
        return self._repo.list_uoms(ctx, company_id=company_id)

    def get_uom(self, ctx: TenantContext, uom_id: UUID):
        uom = self._repo.get_by_id(ctx, uom_id)
        if uom is None:
            raise NotFoundException("UOM not found")
        self._scope.validate_company_access(ctx, uom.company_id)
        return uom

    def create_uom(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        uom_code: str,
        uom_name: str,
        uom_type: str,
        decimal_places: int = 2,
        is_base_uom: bool = False,
    ):
        resolved_company_id = self._scope.resolve_company_id(ctx, company_id)
        self._duplicates.ensure_unique_code(
            model=MasterUom,
            company_id=resolved_company_id,
            code=uom_code,
            code_field="uom_code",
            label="UOM",
        )

        uom = self._repo.create(
            ctx,
            company_id=resolved_company_id,
            uom_code=uom_code,
            uom_name=uom_name,
            uom_type=uom_type,
            decimal_places=decimal_places,
            is_base_uom=is_base_uom,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_uom",
            entity_id=uom.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={"uom_code": uom_code},
        )
        return uom

    def update_uom(self, ctx: TenantContext, uom_id: UUID, **fields):
        self.get_uom(ctx, uom_id)
        updated = self._repo.update(ctx, uom_id, **fields)
        if updated is None:
            raise NotFoundException("UOM not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_uom",
            entity_id=uom_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def delete_uom(self, ctx: TenantContext, uom_id: UUID) -> None:
        self.get_uom(ctx, uom_id)
        if not self._repo.soft_delete(ctx, uom_id):
            raise NotFoundException("UOM not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_uom",
            entity_id=uom_id,
            operation="delete",
            performed_by=ctx.user_id,
        )
