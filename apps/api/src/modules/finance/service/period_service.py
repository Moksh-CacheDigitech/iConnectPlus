"""Accounting period service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.finance.repository.fiscal_repository import FiscalRepository
from modules.finance.service.engines.period_closing_engine import PeriodClosingEngine
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class PeriodService:
    def __init__(self, db: Session) -> None:
        self._repo = FiscalRepository(db)
        self._scope = FinanceScopeValidator(db)
        self._closing = PeriodClosingEngine(db)
        self._audit = AuditService(db)

    def list_periods(
        self, ctx: TenantContext, company_id: UUID | None = None, fiscal_year_id: UUID | None = None
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_periods(ctx, company_id=cid, fiscal_year_id=fiscal_year_id)

    def get_period(self, ctx: TenantContext, period_id: UUID):
        period = self._repo.get_period(ctx, period_id)
        if period is None:
            raise NotFoundException("Period not found")
        self._scope.validate_company_access(ctx, period.company_id)
        return period

    def soft_close(self, ctx: TenantContext, period_id: UUID):
        period = self.get_period(ctx, period_id)
        closed = self._closing.soft_close(ctx, period)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_period",
            entity_id=period_id,
            operation="period_close",
            performed_by=ctx.user_id,
            new_value={"status": "soft_closed"},
        )
        return closed

    def hard_close(self, ctx: TenantContext, period_id: UUID):
        period = self.get_period(ctx, period_id)
        closed = self._closing.hard_close(ctx, period)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_period",
            entity_id=period_id,
            operation="period_close",
            performed_by=ctx.user_id,
            new_value={"status": "hard_closed"},
        )
        return closed

    def reopen(self, ctx: TenantContext, period_id: UUID):
        period = self.get_period(ctx, period_id)
        reopened = self._closing.reopen(ctx, period)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_period",
            entity_id=period_id,
            operation="reopen",
            performed_by=ctx.user_id,
        )
        return reopened

    def update_close_flags(self, ctx: TenantContext, period_id: UUID, **flags):
        self.get_period(ctx, period_id)
        return self._repo.update_period(ctx, period_id, **flags)
