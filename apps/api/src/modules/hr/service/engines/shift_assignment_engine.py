"""ShiftAssignment lifecycle engine."""

from modules.hr.domain.enums import ShiftAssignmentStatus
from modules.hr.domain.exceptions import InvalidShiftAssignmentState


class ShiftAssignmentEngine:
    def submit(self, row) -> None:
        if row.status != ShiftAssignmentStatus.DRAFT.value:
            raise InvalidShiftAssignmentState("Only draft shift assignments can be submitted")
        row.status = ShiftAssignmentStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ShiftAssignmentStatus.SUBMITTED.value:
            raise InvalidShiftAssignmentState("Only submitted shift assignments can be approved")
        row.status = ShiftAssignmentStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != ShiftAssignmentStatus.APPROVED.value:
            raise InvalidShiftAssignmentState("Only approved shift assignments can activate")
        row.status = ShiftAssignmentStatus.ACTIVE.value
