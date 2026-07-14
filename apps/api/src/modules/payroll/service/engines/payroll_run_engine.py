"""PayrollRun lifecycle engine."""

from modules.payroll.domain.enums import (
    PayrollRunStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidPayrollRunState,
)


class PayrollRunEngine:
    def calculate(self, row) -> None:
        if row.status not in {PayrollRunStatus.DRAFT.value}:
            raise InvalidPayrollRunState("Only draft runs can be calculated")
        row.status = PayrollRunStatus.CALCULATED.value

    def submit(self, row) -> None:
        if row.status != PayrollRunStatus.CALCULATED.value:
            raise InvalidPayrollRunState("Only calculated runs can be submitted")
        row.status = PayrollRunStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != PayrollRunStatus.SUBMITTED.value:
            raise InvalidPayrollRunState("Only submitted runs can be approved")
        row.status = PayrollRunStatus.APPROVED.value

    def mark_posted(self, row) -> None:
        if row.status != PayrollRunStatus.APPROVED.value:
            raise InvalidPayrollRunState("Only approved runs can be posted")
        row.status = PayrollRunStatus.POSTED.value

    def mark_paid(self, row) -> None:
        if row.status != PayrollRunStatus.POSTED.value:
            raise InvalidPayrollRunState("Only posted runs can be marked paid")
        row.status = PayrollRunStatus.PAID.value

