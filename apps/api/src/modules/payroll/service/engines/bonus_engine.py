"""Bonus lifecycle engine."""

from modules.payroll.domain.enums import (
    BonusStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidBonusState,
)


class BonusEngine:
    def submit(self, row) -> None:
        if row.status != BonusStatus.DRAFT.value:
            raise InvalidBonusState("Only draft bonus can be submitted")
        row.status = BonusStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != BonusStatus.SUBMITTED.value:
            raise InvalidBonusState("Only submitted bonus can be approved")
        row.status = BonusStatus.APPROVED.value

    def mark_paid(self, row) -> None:
        if row.status != BonusStatus.APPROVED.value:
            raise InvalidBonusState("Only approved bonus can be paid")
        row.status = BonusStatus.PAID.value

