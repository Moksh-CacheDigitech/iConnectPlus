"""TimesheetEntry lifecycle engine."""

from modules.project.domain.enums import (
    TimesheetEntryStatus,
)
from modules.project.domain.exceptions import (
    InvalidTimesheetEntryState,
)


class TimesheetEntryEngine:
    def lock(self, row) -> None:
        if row.status != TimesheetEntryStatus.DRAFT.value:
            raise InvalidTimesheetEntryState("Only draft entries can be locked")
        row.status = TimesheetEntryStatus.LOCKED.value

    def cancel(self, row) -> None:
        if row.status == TimesheetEntryStatus.CANCELLED.value:
            raise InvalidTimesheetEntryState("Entry already cancelled")
        row.status = TimesheetEntryStatus.CANCELLED.value

