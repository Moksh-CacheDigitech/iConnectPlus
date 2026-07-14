"""SalaryComponent lifecycle engine."""

from modules.payroll.domain.enums import (
    ActiveInactive,
)


class SalaryComponentEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value

