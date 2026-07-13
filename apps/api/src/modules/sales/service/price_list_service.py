"""Price list service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.sales.repository.pricing_repository import PricingRepository
from modules.sales.service.sales_scope_validator import SalesScopeValidator


class PriceListService:
    def __init__(self, db: Session) -> None:
        self._repo = PricingRepository(db)
        self._scope = SalesScopeValidator(db)
        self._audit = AuditService(db)

    def list_price_lists(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_price_lists(ctx, cid)

    def get_price_list(self, ctx: TenantContext, price_list_id: UUID):
        row = self._repo.get_price_list(ctx, price_list_id)
        if row is None:
            raise NotFoundException("Price list not found")
        self._scope.validate_company_access(ctx, row.company_id)
        return row

    def create_price_list(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        row = self._repo.create_price_list(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_price_list",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update_price_list(self, ctx: TenantContext, price_list_id: UUID, **fields):
        self.get_price_list(ctx, price_list_id)
        updated = self._repo.update_price_list(ctx, price_list_id, **fields)
        if updated is None:
            raise NotFoundException("Price list not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_price_list",
            entity_id=price_list_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def delete_price_list(self, ctx: TenantContext, price_list_id: UUID) -> None:
        self.get_price_list(ctx, price_list_id)
        if not self._repo.soft_delete_price_list(ctx, price_list_id):
            raise NotFoundException("Price list not found")
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_price_list",
            entity_id=price_list_id,
            operation="delete",
            performed_by=ctx.user_id,
        )

    def add_item(self, ctx: TenantContext, price_list_id: UUID, **fields):
        price_list = self.get_price_list(ctx, price_list_id)
        return self._repo.add_price_list_item(ctx, price_list, **fields)
