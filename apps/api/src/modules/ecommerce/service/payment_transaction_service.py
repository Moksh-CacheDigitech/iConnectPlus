"""PaymentTransactionService application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.ecommerce.models import EcPaymentTransaction
from modules.ecommerce.repository.payment_transaction_repository import PaymentTransactionRepository
from modules.ecommerce.service.ecommerce_scope_validator import EcommerceScopeValidator
from modules.ecommerce.service.engines import PaymentTransactionEngine
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class PaymentTransactionService:
    def __init__(self, db: Session) -> None:
        self._repo = PaymentTransactionRepository(db)
        self._scope = EcommerceScopeValidator(db)
        self._engine = PaymentTransactionEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> EcPaymentTransaction:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("PaymentTransactionService not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        row = self._repo.create(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="ec_payment_transaction",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("PaymentTransactionService not found")
        return row
