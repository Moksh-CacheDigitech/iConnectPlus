"""DesignationAssignment lifecycle engine."""

from modules.hr.domain.enums import AssignmentStatus
from modules.hr.domain.exceptions import InvalidAssignmentState


class DesignationAssignmentEngine:
    def end(self, row) -> None:
        if row.status != AssignmentStatus.ACTIVE.value:
            raise InvalidAssignmentState("Only active assignments can end")
        row.status = AssignmentStatus.ENDED.value
