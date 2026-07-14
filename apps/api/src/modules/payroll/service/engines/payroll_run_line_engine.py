"""PayrollRunLine lifecycle engine."""

from modules.payroll.domain.enums import (
    RunLineStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidPayrollRunLineState,
)


class PayrollRunLineEngine:
    def adjust(self, row) -> None:
        if row.status not in {RunLineStatus.CALCULATED.value, RunLineStatus.ADJUSTED.value}:
            raise InvalidPayrollRunLineState("Line not adjustable")
        row.status = RunLineStatus.ADJUSTED.value

    def lock(self, row) -> None:
        if row.status == RunLineStatus.LOCKED.value:
            raise InvalidPayrollRunLineState("Line already locked")
        row.status = RunLineStatus.LOCKED.value

