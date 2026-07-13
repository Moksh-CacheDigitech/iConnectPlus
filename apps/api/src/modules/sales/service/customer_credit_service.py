"""Customer credit service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.sales.repository.credit_repository import CreditRepository
from modules.sales.service.engines.credit_check_engine import CreditCheckEngine
from modules.sales.service.sales_scope_validator import SalesScopeValidator


class CustomerCreditService:
    def __init__(self, db: Session) -> None:
        self._repo = CreditRepository(db)
        self._scope = SalesScopeValidator(db)
        self._engine = CreditCheckEngine()
        self._audit = AuditService(db)

    def list_credits(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_credits(ctx, cid)

    def get_credit(self, ctx: TenantContext, credit_id: UUID):
        row = self._repo.get_credit(ctx, credit_id)
        if row is None:
            raise NotFoundException("Customer credit not found")
        self._scope.validate_company_access(ctx, row.company_id)
        return row

    def create_credit(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        if fields.get("branch_id"):
            self._scope.validate_branch_access(ctx, fields["branch_id"])
        limit = Decimal(str(fields.get("credit_limit", 0)))
        fields.setdefault("credit_used", 0)
        fields["credit_available"] = float(limit)
        row = self._repo.create_credit(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_customer_credit",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update_credit(self, ctx: TenantContext, credit_id: UUID, **fields):
        self.get_credit(ctx, credit_id)
        updated = self._repo.update_credit(ctx, credit_id, **fields)
        if updated is None:
            raise NotFoundException("Customer credit not found")
        if "credit_limit" in fields:
            self._engine.recalculate_available(updated)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_customer_credit",
            entity_id=credit_id,
            operation="update",
            performed_by=ctx.user_id,
            new_value=fields,
        )
        return updated

    def apply_usage(self, ctx: TenantContext, credit_id: UUID, amount: Decimal):
        credit = self.get_credit(ctx, credit_id)
        used = Decimal(str(credit.credit_used)) + amount
        credit.credit_used = float(used.quantize(Decimal("0.0001")))
        self._engine.recalculate_available(credit)
        return self._repo.update_credit(
            ctx,
            credit_id,
            credit_used=credit.credit_used,
            credit_available=credit.credit_available,
        )

    def release_usage(self, ctx: TenantContext, credit_id: UUID, amount: Decimal):
        credit = self.get_credit(ctx, credit_id)
        used = Decimal(str(credit.credit_used)) - amount
        if used < 0:
            used = Decimal("0")
        credit.credit_used = float(used.quantize(Decimal("0.0001")))
        self._engine.recalculate_available(credit)
        return self._repo.update_credit(
            ctx,
            credit_id,
            credit_used=credit.credit_used,
            credit_available=credit.credit_available,
        )
