"""Payroll reporting service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.repository.payroll_run_repository import PayrollRunRepository
from modules.payroll.repository.payroll_summary_repository import PayrollSummaryRepository
from modules.payroll.service.payroll_scope_validator import PayrollScopeValidator


class PayrollReportService:
    def __init__(self, db: Session) -> None:
        self._scope = PayrollScopeValidator(db)
        self._runs = PayrollRunRepository(db)
        self._summaries = PayrollSummaryRepository(db)

    def payroll_cost_summary(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        runs = self._runs.list_rows(ctx, cid)
        summaries = self._summaries.list_rows(ctx, cid)
        return {
            "run_count": len(runs),
            "summary_count": len(summaries),
            "total_net": sum(float(r.total_net or 0) for r in runs),
        }
