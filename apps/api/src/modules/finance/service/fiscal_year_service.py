"""Fiscal year service."""

from calendar import monthrange
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.finance.domain.enums import FiscalYearStatus
from modules.finance.repository.base import utcnow
from modules.finance.repository.fiscal_repository import FiscalRepository
from modules.finance.service.finance_scope_validator import FinanceScopeValidator
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService


class FiscalYearService:
    def __init__(self, db: Session) -> None:
        self._repo = FiscalRepository(db)
        self._scope = FinanceScopeValidator(db)
        self._audit = AuditService(db)

    def list_fiscal_years(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_fiscal_years(ctx, cid)

    def create_fiscal_year(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID | None = None,
        fiscal_year_code: str,
        fiscal_year_name: str,
        start_date: date,
        end_date: date,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        existing = self._repo.get_open_fiscal_year(ctx, cid)
        if existing:
            raise ConflictException("An open fiscal year already exists for this company")
        fy = self._repo.create_fiscal_year(
            ctx,
            company_id=cid,
            fiscal_year_code=fiscal_year_code,
            fiscal_year_name=fiscal_year_name,
            start_date=start_date,
            end_date=end_date,
            status=FiscalYearStatus.OPEN.value,
        )
        self._generate_periods(ctx, fy, cid)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_fiscal_year",
            entity_id=fy.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return fy

    def _generate_periods(self, ctx: TenantContext, fy, company_id: UUID) -> None:
        current = fy.start_date
        for period_num in range(1, 13):
            if current > fy.end_date:
                break
            last_day = monthrange(current.year, current.month)[1]
            period_end = date(current.year, current.month, last_day)
            if period_end > fy.end_date:
                period_end = fy.end_date
            self._repo.create_period(
                ctx,
                company_id=company_id,
                fiscal_year_id=fy.id,
                period_number=period_num,
                period_name=current.strftime("%b-%Y"),
                start_date=current,
                end_date=period_end,
                status="open",
            )
            current = period_end + timedelta(days=1)

    def close_fiscal_year(self, ctx: TenantContext, fiscal_year_id: UUID):
        fy = self._repo.get_fiscal_year(ctx, fiscal_year_id)
        if fy is None:
            raise NotFoundException("Fiscal year not found")
        periods = self._repo.list_periods(ctx, company_id=fy.company_id, fiscal_year_id=fy.id)
        if any(p.status != "hard_closed" for p in periods):
            raise ConflictException("All periods must be hard closed before year close")
        fy.status = FiscalYearStatus.CLOSED.value
        fy.closed_at = utcnow()
        fy.closed_by = ctx.user_id
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="fin_fiscal_year",
            entity_id=fy.id,
            operation="year_close",
            performed_by=ctx.user_id,
        )
        return fy
