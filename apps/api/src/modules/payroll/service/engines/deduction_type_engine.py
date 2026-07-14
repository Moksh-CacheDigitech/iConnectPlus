"""DeductionType lifecycle engine."""

from modules.payroll.domain.enums import (
    ActiveInactive,
)


class DeductionTypeEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value

