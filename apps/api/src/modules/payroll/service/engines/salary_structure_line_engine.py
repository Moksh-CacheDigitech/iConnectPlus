"""SalaryStructureLine lifecycle engine."""

from modules.payroll.domain.enums import (
    ActiveInactive,
)


class SalaryStructureLineEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value

