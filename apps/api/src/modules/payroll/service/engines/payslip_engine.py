"""Payslip lifecycle engine."""

from modules.payroll.domain.enums import (
    PayslipStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidPayslipState,
)


class PayslipEngine:
    def issue(self, row) -> None:
        if row.status != PayslipStatus.GENERATED.value:
            raise InvalidPayslipState("Only generated payslips can be issued")
        row.status = PayslipStatus.ISSUED.value

    def void(self, row) -> None:
        if row.status == PayslipStatus.VOID.value:
            raise InvalidPayslipState("Payslip already void")
        row.status = PayslipStatus.VOID.value

