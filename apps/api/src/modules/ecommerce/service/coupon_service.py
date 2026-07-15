"""CouponService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.ecommerce.domain.enums import EcommerceEntityType
from modules.ecommerce.models import EcCoupon
from modules.ecommerce.repository.coupon_repository import CouponRepository
from modules.ecommerce.service.ecommerce_number_service import EcommerceNumberService
from modules.ecommerce.service.ecommerce_scope_validator import EcommerceScopeValidator
from modules.ecommerce.service.engines import CouponEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class CouponService:
    def __init__(self, db: Session) -> None:
        self._repo = CouponRepository(db)
        self._scope = EcommerceScopeValidator(db)
        self._numbers = EcommerceNumberService(db)
        self._engine = CouponEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> EcCoupon:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("CouponService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(EcommerceEntityType.COUPON, cid, EcCoupon, "coupon_number")
        return self._repo.create(ctx, company_id=cid, coupon_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("CouponService not found")
        return row

