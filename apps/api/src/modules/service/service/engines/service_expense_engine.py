"""ServiceExpense lifecycle engine."""

from modules.service.domain.enums import (
    ServiceExpenseStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceExpenseState,
)


class ServiceExpenseEngine:
    def submit(self, row) -> None:
        if row.status != ServiceExpenseStatus.DRAFT.value:
            raise InvalidServiceExpenseState("Only draft expenses can be submitted")
        row.status = ServiceExpenseStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceExpenseStatus.SUBMITTED.value:
            raise InvalidServiceExpenseState("Only submitted expenses can be approved")
        row.status = ServiceExpenseStatus.APPROVED.value

    def post(self, row) -> None:
        if row.status != ServiceExpenseStatus.APPROVED.value:
            raise InvalidServiceExpenseState("Only approved expenses can be posted")
        row.status = ServiceExpenseStatus.POSTED.value

    def cancel(self, row) -> None:
        if row.status == ServiceExpenseStatus.POSTED.value:
            raise InvalidServiceExpenseState("Posted expenses cannot be cancelled")
        row.status = ServiceExpenseStatus.CANCELLED.value

