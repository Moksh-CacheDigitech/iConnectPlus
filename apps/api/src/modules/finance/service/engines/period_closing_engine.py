"""Period closing engine."""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from modules.finance.domain.enums import PeriodStatus
from modules.finance.domain.exceptions import JournalStateError, PeriodClosed
from modules.finance.models.fiscal import FinPeriod
from modules.finance.repository.fiscal_repository import FiscalRepository
from modules.finance.repository.journal_repository import JournalRepository
from modules.foundation.domain.value_objects import TenantContext


class PeriodClosingEngine:
    def __init__(self, db: Session) -> None:
        self._fiscal = FiscalRepository(db)
        self._journal = JournalRepository(db)

    def soft_close(self, ctx: TenantContext, period: FinPeriod) -> FinPeriod:
        if period.status == PeriodStatus.HARD_CLOSED.value:
            raise PeriodClosed("Period is already hard closed")
        open_count = self._journal.count_open_journals_in_period(ctx, period.id)
        if open_count > 0:
            raise JournalStateError("Cannot close period with open journals")
        period.status = PeriodStatus.SOFT_CLOSED.value
        period.closed_at = datetime.now(timezone.utc)
        period.closed_by = ctx.user_id
        self._fiscal.update_period(ctx, period.id, status=period.status, closed_at=period.closed_at, closed_by=period.closed_by)
        return period

    def hard_close(self, ctx: TenantContext, period: FinPeriod) -> FinPeriod:
        if period.status == PeriodStatus.HARD_CLOSED.value:
            raise PeriodClosed("Period is already hard closed")
        if not all([period.ar_closed, period.ap_closed, period.gl_closed]):
            raise JournalStateError(
                "All sub-module close flags (AR, AP, GL) must be set before hard close"
            )
        open_count = self._journal.count_open_journals_in_period(ctx, period.id)
        if open_count > 0:
            raise JournalStateError("Cannot hard close period with open journals")
        period.status = PeriodStatus.HARD_CLOSED.value
        period.gl_closed = True
        period.closed_at = datetime.now(timezone.utc)
        period.closed_by = ctx.user_id
        self._fiscal.update_period(
            ctx,
            period.id,
            status=period.status,
            gl_closed=True,
            closed_at=period.closed_at,
            closed_by=period.closed_by,
        )
        return period

    def reopen(self, ctx: TenantContext, period: FinPeriod) -> FinPeriod:
        if period.status == PeriodStatus.OPEN.value:
            return period
        period.status = PeriodStatus.OPEN.value
        period.ar_closed = False
        period.ap_closed = False
        period.inventory_closed = False
        period.payroll_closed = False
        period.gl_closed = False
        period.closed_at = None
        period.closed_by = None
        self._fiscal.update_period(
            ctx,
            period.id,
            status=period.status,
            ar_closed=False,
            ap_closed=False,
            inventory_closed=False,
            payroll_closed=False,
            gl_closed=False,
            closed_at=None,
            closed_by=None,
        )
        return period
