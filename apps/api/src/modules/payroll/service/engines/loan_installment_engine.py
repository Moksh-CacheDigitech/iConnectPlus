"""LoanInstallment lifecycle engine."""

from modules.payroll.domain.enums import (
    LoanInstallmentStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidLoanInstallmentState,
)


class LoanInstallmentEngine:
    def recover(self, row) -> None:
        if row.status != LoanInstallmentStatus.SCHEDULED.value:
            raise InvalidLoanInstallmentState("Only scheduled installments can be recovered")
        row.status = LoanInstallmentStatus.RECOVERED.value

    def waive(self, row) -> None:
        if row.status not in {LoanInstallmentStatus.SCHEDULED.value, LoanInstallmentStatus.OVERDUE.value}:
            raise InvalidLoanInstallmentState("Installment cannot be waived")
        row.status = LoanInstallmentStatus.WAIVED.value

