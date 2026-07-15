"""PaymentService."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.ecommerce.domain.enums import EcommerceEntityType
from modules.ecommerce.models import EcPayment
from modules.ecommerce.repository.payment_repository import PaymentRepository
from modules.ecommerce.service.ecommerce_number_service import EcommerceNumberService
from modules.ecommerce.service.ecommerce_scope_validator import EcommerceScopeValidator
from modules.ecommerce.service.engines import PaymentEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class PaymentService:
    def __init__(self, db: Session) -> None:
        self._repo = PaymentRepository(db)
        self._scope = EcommerceScopeValidator(db)
        self._numbers = EcommerceNumberService(db)
        self._engine = PaymentEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> EcPayment:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("PaymentService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(EcommerceEntityType.PAYMENT, cid, EcPayment, "payment_number")
        return self._repo.create(ctx, company_id=cid, payment_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("PaymentService not found")
        return row

    def capture(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.capture(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def refund(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.refund(row)
        return self._repo.update(ctx, row_id, status=row.status)

