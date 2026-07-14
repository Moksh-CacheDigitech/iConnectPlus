"""Attendance lifecycle engine."""

from modules.hr.domain.enums import AttendanceRecordStatus
from modules.hr.domain.exceptions import InvalidAttendanceState


class AttendanceEngine:
    def adjust(self, row) -> None:
        if row.status == AttendanceRecordStatus.LOCKED.value:
            raise InvalidAttendanceState("Locked attendance cannot be adjusted")
        row.status = AttendanceRecordStatus.ADJUSTED.value

    def lock(self, row) -> None:
        if row.status == AttendanceRecordStatus.LOCKED.value:
            raise InvalidAttendanceState("Attendance already locked")
        row.status = AttendanceRecordStatus.LOCKED.value
