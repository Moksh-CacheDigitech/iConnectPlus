"""EmployeeSalaryComponent lifecycle engine."""

from modules.payroll.domain.enums import (
    ActiveInactive,
)


class EmployeeSalaryComponentEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value

