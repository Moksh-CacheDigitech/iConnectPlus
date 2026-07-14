"""PayrollAdjustment lifecycle engine."""

from modules.payroll.domain.enums import (
    AdjustmentStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidPayrollAdjustmentState,
)


class PayrollAdjustmentEngine:
    def apply(self, row) -> None:
        if row.status != AdjustmentStatus.DRAFT.value:
            raise InvalidPayrollAdjustmentState("Only draft adjustments can be applied")
        row.status = AdjustmentStatus.APPLIED.value

