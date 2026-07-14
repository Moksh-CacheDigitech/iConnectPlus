"""LeaveType lifecycle engine."""

from modules.hr.domain.enums import ActiveInactive


class LeaveTypeEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
