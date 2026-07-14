"""Timesheet lifecycle engine."""

from modules.project.domain.enums import (
    TimesheetStatus,
)
from modules.project.domain.exceptions import (
    InvalidTimesheetState,
)


class TimesheetEngine:
    def submit(self, row) -> None:
        if row.status != TimesheetStatus.DRAFT.value:
            raise InvalidTimesheetState("Only draft timesheets can be submitted")
        row.status = TimesheetStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != TimesheetStatus.SUBMITTED.value:
            raise InvalidTimesheetState("Only submitted timesheets can be approved")
        row.status = TimesheetStatus.APPROVED.value

    def reject(self, row) -> None:
        if row.status != TimesheetStatus.SUBMITTED.value:
            raise InvalidTimesheetState("Only submitted timesheets can be rejected")
        row.status = TimesheetStatus.REJECTED.value

    def cancel(self, row) -> None:
        if row.status in {TimesheetStatus.APPROVED.value, TimesheetStatus.CANCELLED.value}:
            raise InvalidTimesheetState("Timesheet already terminal")
        row.status = TimesheetStatus.CANCELLED.value

