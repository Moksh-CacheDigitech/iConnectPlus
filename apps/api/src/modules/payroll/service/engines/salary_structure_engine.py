"""SalaryStructure lifecycle engine."""

from modules.payroll.domain.enums import (
    SalaryStructureStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidSalaryStructureState,
)


class SalaryStructureEngine:
    def activate(self, row) -> None:
        if row.status not in {SalaryStructureStatus.DRAFT.value, SalaryStructureStatus.INACTIVE.value}:
            raise InvalidSalaryStructureState("Structure not activatable")
        row.status = SalaryStructureStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        if row.status != SalaryStructureStatus.ACTIVE.value:
            raise InvalidSalaryStructureState("Only active structures can be deactivated")
        row.status = SalaryStructureStatus.INACTIVE.value

