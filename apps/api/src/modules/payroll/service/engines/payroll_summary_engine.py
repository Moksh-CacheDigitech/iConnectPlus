"""PayrollSummary lifecycle engine."""

from modules.payroll.domain.enums import (
    SummaryStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidPayrollSummaryState,
)


class PayrollSummaryEngine:
    def finalize(self, row) -> None:
        if row.status != SummaryStatus.DRAFT.value:
            raise InvalidPayrollSummaryState("Only draft summaries can finalize")
        row.status = SummaryStatus.FINALIZED.value

