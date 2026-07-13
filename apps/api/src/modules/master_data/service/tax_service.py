"""Tax service."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.master_data.domain.enums import MasterEntityType
from modules.master_data.models.reference import MasterTax
from modules.master_data.repository.tax_repository import TaxRepository
from modules.master_data.service.code_generator_service import CodeGeneratorService
from modules.master_data.service.duplicate_checker_service import DuplicateCheckerService
from modules.master_data.service.master_scope_validator import MasterScopeValidator


class TaxService:
    def __init__(self, db: Session) -> None:
        self._repo = TaxRepository(db)
        self._audit = AuditService(db)
        self._codes = CodeGeneratorService(db)
        self._duplicates = DuplicateCheckerService(db)
        self._scope = MasterScopeValidator(db)

    def list_taxes(self, ctx: TenantContext, *, company_id: UUID | None = None):
        if company_id:
            self._scope.validate_company_access(ctx, company_id)
        return self._repo.list_taxes(ctx, company_id=company_id)

    def get_tax(self, ctx: TenantContext, tax_id: UUID):
        tax = self._repo.get_by_id(ctx, tax_id)
        if tax is None:
            raise NotFoundException("Tax not found")
        self._scope.validate_company_access(ctx, tax.company_id)
        return tax

    def create_tax(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        tax_code: str | None = None,
        tax_name: str,
        tax_type: str,
        rate_percent: float,
        effective_from: date,
        is_compound: bool = False,
        effective_to: date | None = None,
    ):
        resolved_company_id = self._scope.resolve_company_id(ctx, company_id)

        if tax_code is None:
            tax_code = self._codes.generate(
                MasterEntityType.TAX,
                resolved_company_id,
                model=MasterTax,
                code_column="tax_code",
            )
        else:
            self._duplicates.ensure_unique_code(
                model=MasterTax,
                company_id=resolved_company_id,
                code=tax_code,
                code_field="tax_code",
                label="Tax",
            )

        tax = self._repo.create(
            ctx,
            company_id=resolved_company_id,
            tax_code=tax_code,
            tax_name=tax_name,
            tax_type=tax_type,
            rate_percent=rate_percent,
            effective_from=effective_from,
            is_compound=is_compound,
            effective_to=effective_to,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_tax",
            entity_id=tax.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={"tax_code": tax_code},
        )
        return tax

    def update_tax(self, ctx: TenantContext, tax_id: UUID, **fields):
        self.get_tax(ctx, tax_id)
        updated = self._repo.update(ctx, tax_id, **fields)
        if updated is None:
            raise NotFoundException("Tax not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_tax",
            entity_id=tax_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def delete_tax(self, ctx: TenantContext, tax_id: UUID) -> None:
        self.get_tax(ctx, tax_id)
        if not self._repo.soft_delete(ctx, tax_id):
            raise NotFoundException("Tax not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="master_tax",
            entity_id=tax_id,
            operation="delete",
            performed_by=ctx.user_id,
        )
