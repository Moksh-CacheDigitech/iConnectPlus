"""Reimbursement lifecycle engine."""

from modules.payroll.domain.enums import (
    ReimbursementStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidReimbursementState,
)


class ReimbursementEngine:
    def submit(self, row) -> None:
        if row.status != ReimbursementStatus.DRAFT.value:
            raise InvalidReimbursementState("Only draft reimbursement can be submitted")
        row.status = ReimbursementStatus.SUBMITTED.value

    def manager_approve(self, row) -> None:
        if row.status != ReimbursementStatus.SUBMITTED.value:
            raise InvalidReimbursementState("Only submitted reimbursement can be manager approved")
        row.status = ReimbursementStatus.MANAGER_APPROVED.value

    def finance_approve(self, row) -> None:
        if row.status != ReimbursementStatus.MANAGER_APPROVED.value:
            raise InvalidReimbursementState("Manager approval required")
        row.status = ReimbursementStatus.FINANCE_APPROVED.value

