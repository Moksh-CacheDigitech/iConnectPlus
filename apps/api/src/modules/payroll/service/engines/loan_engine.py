"""Loan lifecycle engine."""

from modules.payroll.domain.enums import (
    LoanStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidLoanState,
)


class LoanEngine:
    def submit(self, row) -> None:
        if row.status != LoanStatus.DRAFT.value:
            raise InvalidLoanState("Only draft loans can be submitted")
        row.status = LoanStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != LoanStatus.SUBMITTED.value:
            raise InvalidLoanState("Only submitted loans can be approved")
        row.status = LoanStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != LoanStatus.APPROVED.value:
            raise InvalidLoanState("Only approved loans can activate")
        row.status = LoanStatus.ACTIVE.value

    def close(self, row) -> None:
        if row.status != LoanStatus.ACTIVE.value:
            raise InvalidLoanState("Only active loans can close")
        row.status = LoanStatus.CLOSED.value

