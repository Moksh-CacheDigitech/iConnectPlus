"""PromotionService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.ecommerce.domain.enums import EcommerceEntityType
from modules.ecommerce.models import EcPromotion
from modules.ecommerce.repository.promotion_repository import PromotionRepository
from modules.ecommerce.service.ecommerce_number_service import EcommerceNumberService
from modules.ecommerce.service.ecommerce_scope_validator import EcommerceScopeValidator
from modules.ecommerce.service.engines import PromotionEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class PromotionService:
    def __init__(self, db: Session) -> None:
        self._repo = PromotionRepository(db)
        self._scope = EcommerceScopeValidator(db)
        self._numbers = EcommerceNumberService(db)
        self._engine = PromotionEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> EcPromotion:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("PromotionService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(EcommerceEntityType.PROMOTION, cid, EcPromotion, "promotion_number")
        return self._repo.create(ctx, company_id=cid, promotion_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("PromotionService not found")
        return row

