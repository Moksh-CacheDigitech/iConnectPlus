"""ProductListingService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.ecommerce.domain.enums import EcommerceEntityType
from modules.ecommerce.models import EcProductListing
from modules.ecommerce.repository.product_listing_repository import ProductListingRepository
from modules.ecommerce.service.ecommerce_number_service import EcommerceNumberService
from modules.ecommerce.service.ecommerce_scope_validator import EcommerceScopeValidator
from modules.ecommerce.service.engines import ProductListingEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class ProductListingService:
    def __init__(self, db: Session) -> None:
        self._repo = ProductListingRepository(db)
        self._scope = EcommerceScopeValidator(db)
        self._numbers = EcommerceNumberService(db)
        self._engine = ProductListingEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> EcProductListing:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("ProductListingService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(EcommerceEntityType.PRODUCT_LISTING, cid, EcProductListing, "listing_number")
        return self._repo.create(ctx, company_id=cid, listing_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("ProductListingService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def publish(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.publish(row)
        return self._repo.update(ctx, row_id, status=row.status)

