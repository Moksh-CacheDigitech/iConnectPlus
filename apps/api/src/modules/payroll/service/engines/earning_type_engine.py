"""EarningType lifecycle engine."""

from modules.payroll.domain.enums import (
    ActiveInactive,
)


class EarningTypeEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value

