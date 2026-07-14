"""StatutoryContribution lifecycle engine."""

from modules.payroll.domain.enums import (
    ActiveInactive,
)


class StatutoryContributionEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value

