"""Payroll port for HR separation / FNF — reads payroll facts, writes via payroll repos."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.models import PayPayrollPeriod, PayPayrollRunLine
from modules.payroll.repository.payroll_run_line_repository import PayrollRunLineRepository


class HrPayrollAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_open_period(self, company_id: UUID) -> PayPayrollPeriod | None:
        return self._db.scalar(
            select(PayPayrollPeriod)
            .where(
                PayPayrollPeriod.company_id == company_id,
                PayPayrollPeriod.is_deleted.is_(False),
                PayPayrollPeriod.status.in_(("open", "processing")),
            )
            .order_by(PayPayrollPeriod.start_date.desc())
        )

    def find_run_line(self, run_id: UUID, employee_id: UUID) -> PayPayrollRunLine | None:
        return self._db.scalar(
            select(PayPayrollRunLine).where(
                PayPayrollRunLine.payroll_run_id == run_id,
                PayPayrollRunLine.employee_id == employee_id,
                PayPayrollRunLine.is_deleted.is_(False),
            )
        )

    def add_fnf_components(
        self,
        ctx: TenantContext,
        line_id: UUID,
        *,
        extra: Decimal,
        breakdown_updates: dict,
    ) -> None:
        repo = PayrollRunLineRepository(self._db)
        line = repo.get(ctx, line_id)
        if line is None:
            return
        breakdown = dict(line.component_breakdown_json or {})
        breakdown.update(breakdown_updates)
        repo.update(
            ctx,
            line_id,
            component_breakdown_json=breakdown,
            gross_earnings=Decimal(str(line.gross_earnings or 0)) + extra,
            net_pay=Decimal(str(line.net_pay or 0)) + extra,
        )
