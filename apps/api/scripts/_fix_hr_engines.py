"""Rewrite HR engine files with minimal imports."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENG = ROOT / "src" / "modules" / "hr" / "service" / "engines"


def w(name: str, content: str) -> None:
    path = ENG / name
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    print("fixed", name)


ENGINES = {
    "designation_engine.py": '''"""Designation lifecycle engine."""

from modules.hr.domain.enums import ActiveInactive
from modules.hr.domain.exceptions import InvalidDesignationState


class DesignationEngine:
    def validate_active(self, row) -> None:
        if row.status not in {"active", "inactive"}:
            raise InvalidDesignationState("Invalid designation status")

    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "employee_profile_engine.py": '''"""EmployeeProfile lifecycle engine."""

from modules.hr.domain.enums import ActiveInactive
from modules.hr.domain.exceptions import InvalidEmployeeProfileState


class EmployeeProfileEngine:
    def validate_writable(self, row) -> None:
        if row.status == ActiveInactive.INACTIVE.value:
            raise InvalidEmployeeProfileState("Inactive profile cannot be updated for ESS changes")
''',
    "employment_engine.py": '''"""Employment lifecycle engine."""

from modules.hr.domain.enums import EmploymentStatus
from modules.hr.domain.exceptions import InvalidEmploymentState


class EmploymentEngine:
    ACTIVE_SET = {"active", "probation", "confirmed"}

    def validate_activate(self, row) -> None:
        if row.status not in {"draft", "probation"}:
            raise InvalidEmploymentState("Employment must be draft/probation to activate")

    def apply_activate(self, row) -> None:
        self.validate_activate(row)
        row.status = EmploymentStatus.ACTIVE.value

    def apply_confirm(self, row) -> None:
        if row.status not in {"active", "probation"}:
            raise InvalidEmploymentState("Only active/probation employment can be confirmed")
        row.status = EmploymentStatus.CONFIRMED.value

    def apply_end(self, row) -> None:
        if row.status not in self.ACTIVE_SET:
            raise InvalidEmploymentState("Only active employment can be ended")
        row.status = EmploymentStatus.ENDED.value
''',
    "department_assignment_engine.py": '''"""DepartmentAssignment lifecycle engine."""

from modules.hr.domain.enums import AssignmentStatus
from modules.hr.domain.exceptions import InvalidAssignmentState


class DepartmentAssignmentEngine:
    def end(self, row) -> None:
        if row.status != AssignmentStatus.ACTIVE.value:
            raise InvalidAssignmentState("Only active assignments can end")
        row.status = AssignmentStatus.ENDED.value
''',
    "designation_assignment_engine.py": '''"""DesignationAssignment lifecycle engine."""

from modules.hr.domain.enums import AssignmentStatus
from modules.hr.domain.exceptions import InvalidAssignmentState


class DesignationAssignmentEngine:
    def end(self, row) -> None:
        if row.status != AssignmentStatus.ACTIVE.value:
            raise InvalidAssignmentState("Only active assignments can end")
        row.status = AssignmentStatus.ENDED.value
''',
    "shift_engine.py": '''"""Shift lifecycle engine."""

from modules.hr.domain.enums import ActiveInactive


class ShiftEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "shift_assignment_engine.py": '''"""ShiftAssignment lifecycle engine."""

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
''',
    "holiday_calendar_engine.py": '''"""HolidayCalendar lifecycle engine."""

from modules.hr.domain.enums import HolidayCalendarStatus
from modules.hr.domain.exceptions import InvalidHolidayCalendarState


class HolidayCalendarEngine:
    def publish(self, row) -> None:
        if row.status != HolidayCalendarStatus.DRAFT.value:
            raise InvalidHolidayCalendarState("Only draft calendars can be published")
        row.status = HolidayCalendarStatus.PUBLISHED.value

    def archive(self, row) -> None:
        if row.status != HolidayCalendarStatus.PUBLISHED.value:
            raise InvalidHolidayCalendarState("Only published calendars can be archived")
        row.status = HolidayCalendarStatus.ARCHIVED.value
''',
    "leave_type_engine.py": '''"""LeaveType lifecycle engine."""

from modules.hr.domain.enums import ActiveInactive


class LeaveTypeEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "leave_balance_engine.py": '''"""LeaveBalance lifecycle engine."""

from decimal import Decimal

from modules.hr.domain.enums import LeaveBalanceStatus
from modules.hr.domain.exceptions import InvalidLeaveBalanceState


class LeaveBalanceEngine:
    def apply_usage(self, row, days) -> None:
        if row.status != LeaveBalanceStatus.OPEN.value:
            raise InvalidLeaveBalanceState("Leave balance is closed")
        used = Decimal(str(row.used or 0)) + Decimal(str(days))
        closing = Decimal(str(row.opening_balance or 0)) + Decimal(str(row.accrued or 0)) - used
        if closing < 0:
            raise InvalidLeaveBalanceState("Insufficient leave balance")
        row.used = used
        row.closing_balance = closing

    def accrue(self, row, days) -> None:
        if row.status != LeaveBalanceStatus.OPEN.value:
            raise InvalidLeaveBalanceState("Leave balance is closed")
        row.accrued = Decimal(str(row.accrued or 0)) + Decimal(str(days))
        row.closing_balance = (
            Decimal(str(row.opening_balance or 0))
            + Decimal(str(row.accrued or 0))
            - Decimal(str(row.used or 0))
        )
''',
    "leave_request_engine.py": '''"""LeaveRequest lifecycle engine."""

from modules.hr.domain.enums import LeaveRequestStatus
from modules.hr.domain.exceptions import InvalidLeaveRequestState


class LeaveRequestEngine:
    def submit(self, row) -> None:
        if row.status != LeaveRequestStatus.DRAFT.value:
            raise InvalidLeaveRequestState("Only draft leave requests can be submitted")
        row.status = LeaveRequestStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != LeaveRequestStatus.SUBMITTED.value:
            raise InvalidLeaveRequestState("Only submitted leave can be approved")
        row.status = LeaveRequestStatus.APPROVED.value

    def reject(self, row) -> None:
        if row.status != LeaveRequestStatus.SUBMITTED.value:
            raise InvalidLeaveRequestState("Only submitted leave can be rejected")
        row.status = LeaveRequestStatus.REJECTED.value

    def cancel(self, row) -> None:
        if row.status in {LeaveRequestStatus.APPROVED.value, LeaveRequestStatus.CANCELLED.value}:
            raise InvalidLeaveRequestState("Cannot cancel approved/cancelled leave")
        row.status = LeaveRequestStatus.CANCELLED.value
''',
    "attendance_engine.py": '''"""Attendance lifecycle engine."""

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
''',
    "employee_document_engine.py": '''"""EmployeeDocument lifecycle engine."""

from modules.hr.domain.enums import DocumentStatus, VerificationStatus
from modules.hr.domain.exceptions import InvalidEmployeeDocumentState


class EmployeeDocumentEngine:
    def verify(self, row) -> None:
        if row.verification_status == VerificationStatus.VERIFIED.value:
            raise InvalidEmployeeDocumentState("Document already verified")
        row.verification_status = VerificationStatus.VERIFIED.value

    def reject(self, row) -> None:
        row.verification_status = VerificationStatus.REJECTED.value

    def archive(self, row) -> None:
        row.status = DocumentStatus.ARCHIVED.value
''',
    "performance_review_engine.py": '''"""PerformanceReview lifecycle engine."""

from modules.hr.domain.enums import PerformanceReviewStatus
from modules.hr.domain.exceptions import InvalidPerformanceReviewState


class PerformanceReviewEngine:
    def start(self, row) -> None:
        if row.status != PerformanceReviewStatus.DRAFT.value:
            raise InvalidPerformanceReviewState("Only draft reviews can start")
        row.status = PerformanceReviewStatus.IN_PROGRESS.value

    def submit(self, row) -> None:
        if row.status not in {
            PerformanceReviewStatus.DRAFT.value,
            PerformanceReviewStatus.IN_PROGRESS.value,
        }:
            raise InvalidPerformanceReviewState("Review not submittable")
        row.status = PerformanceReviewStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != PerformanceReviewStatus.SUBMITTED.value:
            raise InvalidPerformanceReviewState("Only submitted reviews can be approved")
        row.status = PerformanceReviewStatus.APPROVED.value

    def close(self, row) -> None:
        if row.status != PerformanceReviewStatus.APPROVED.value:
            raise InvalidPerformanceReviewState("Only approved reviews can be closed")
        row.status = PerformanceReviewStatus.CLOSED.value
''',
    "goal_engine.py": '''"""Goal lifecycle engine."""

from modules.hr.domain.enums import GoalStatus
from modules.hr.domain.exceptions import InvalidGoalState


class GoalEngine:
    def achieve(self, row) -> None:
        if row.status != GoalStatus.OPEN.value:
            raise InvalidGoalState("Only open goals can be achieved")
        row.status = GoalStatus.ACHIEVED.value

    def miss(self, row) -> None:
        if row.status != GoalStatus.OPEN.value:
            raise InvalidGoalState("Only open goals can be missed")
        row.status = GoalStatus.MISSED.value
''',
    "appraisal_engine.py": '''"""Appraisal lifecycle engine."""

from modules.hr.domain.enums import AppraisalStatus
from modules.hr.domain.exceptions import InvalidAppraisalState


class AppraisalEngine:
    def finalize(self, row) -> None:
        if row.status != AppraisalStatus.DRAFT.value:
            raise InvalidAppraisalState("Only draft appraisals can be finalized")
        row.status = AppraisalStatus.FINAL.value
''',
    "training_engine.py": '''"""Training lifecycle engine."""

from modules.hr.domain.enums import TrainingStatus
from modules.hr.domain.exceptions import InvalidTrainingState


class TrainingEngine:
    def start(self, row) -> None:
        if row.status != TrainingStatus.PLANNED.value:
            raise InvalidTrainingState("Only planned training can start")
        row.status = TrainingStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status not in {TrainingStatus.PLANNED.value, TrainingStatus.IN_PROGRESS.value}:
            raise InvalidTrainingState("Training cannot be completed from current status")
        row.status = TrainingStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status == TrainingStatus.COMPLETED.value:
            raise InvalidTrainingState("Completed training cannot be cancelled")
        row.status = TrainingStatus.CANCELLED.value
''',
    "training_attendance_engine.py": '''"""TrainingAttendance lifecycle engine."""

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
''',
    "separation_engine.py": '''"""Separation lifecycle engine."""

from modules.hr.domain.enums import SeparationStatus
from modules.hr.domain.exceptions import InvalidSeparationState


class SeparationEngine:
    def submit(self, row) -> None:
        if row.status != SeparationStatus.DRAFT.value:
            raise InvalidSeparationState("Only draft separations can be submitted")
        row.status = SeparationStatus.SUBMITTED.value

    def manager_approve(self, row) -> None:
        if row.status != SeparationStatus.SUBMITTED.value:
            raise InvalidSeparationState("Only submitted separations can receive manager approval")
        row.status = SeparationStatus.MANAGER_APPROVED.value

    def hr_approve(self, row) -> None:
        if row.status != SeparationStatus.MANAGER_APPROVED.value:
            raise InvalidSeparationState("Manager approval required before HR approval")
        row.status = SeparationStatus.HR_APPROVED.value

    def complete(self, row) -> None:
        if row.status != SeparationStatus.HR_APPROVED.value:
            raise InvalidSeparationState("HR approval required before completion")
        row.status = SeparationStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status == SeparationStatus.COMPLETED.value:
            raise InvalidSeparationState("Completed separation cannot be cancelled")
        row.status = SeparationStatus.CANCELLED.value
''',
}


def main() -> None:
    for name, content in ENGINES.items():
        w(name, content)


if __name__ == "__main__":
    main()
