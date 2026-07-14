"""TrainingAttendance lifecycle engine."""

from modules.hr.domain.enums import TrainingAttendanceRecordStatus, TrainingAttendanceStatus
from modules.hr.domain.exceptions import InvalidTrainingAttendanceState


class TrainingAttendanceEngine:
    def mark_attended(self, row) -> None:
        if row.status != TrainingAttendanceRecordStatus.ACTIVE.value:
            raise InvalidTrainingAttendanceState("Cancelled attendance cannot be updated")
        row.attendance_status = TrainingAttendanceStatus.ATTENDED.value

    def mark_completed(self, row) -> None:
        if row.status != TrainingAttendanceRecordStatus.ACTIVE.value:
            raise InvalidTrainingAttendanceState("Cancelled attendance cannot be updated")
        row.attendance_status = TrainingAttendanceStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = TrainingAttendanceRecordStatus.CANCELLED.value
