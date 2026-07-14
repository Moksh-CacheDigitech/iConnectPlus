"""Generate Sprint 11 HRMS module artifacts. Run from apps/api: python scripts/_gen_hr_sprint11.py"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
HR = SRC / "modules" / "hr"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = SRC / "tests"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n") if content.startswith("\n") else content, encoding="utf-8")
    if not content.endswith("\n"):
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Scaffold package
# ---------------------------------------------------------------------------

w(HR / "__init__.py", '"""Human Resource Management (HRMS) module — Sprint 11."""\n')
w(HR / "domain" / "__init__.py", '"""HR domain layer."""\n')
w(HR / "adapters" / "__init__.py", '"""HR cross-module adapters."""\n')
w(HR / "service" / "__init__.py", '"""HR services — populated after generation."""\n')
w(HR / "service" / "engines" / "__init__.py", '"""HR engines — populated after generation."""\n')
w(HR / "repository" / "__init__.py", '"""HR repositories."""\n')
w(HR / "models" / "__init__.py", '"""HR models — populated after generation."""\n')

w(
    HR / "models" / "mixins.py",
    '''
"""HR ORM mixin bundles per ERD_11."""

from database.mixins import (
    AuditMixin,
    BranchMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

HrMasterMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)

HrTransactionMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    BranchMixin,
    SoftDeleteMixin,
    VersionMixin,
)

HrDetailMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    BranchMixin,
    SoftDeleteMixin,
    VersionMixin,
)
''',
)

w(
    HR / "domain" / "enums.py",
    '''
"""HR domain enums per ERD_11."""

from enum import Enum


class ActiveInactive(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class JobLevel(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXEC = "exec"


class EmploymentType(str, Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    INTERN = "intern"
    CONSULTANT = "consultant"


class EmploymentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PROBATION = "probation"
    CONFIRMED = "confirmed"
    ENDED = "ended"
    CANCELLED = "cancelled"


class AssignmentStatus(str, Enum):
    ACTIVE = "active"
    ENDED = "ended"


class ShiftType(str, Enum):
    GENERAL = "general"
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"
    ROTATIONAL = "rotational"


class ShiftAssignmentStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    ENDED = "ended"
    CANCELLED = "cancelled"


class HolidayCalendarStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class LeaveRequestStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveBalanceStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class AttendanceDayStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    WORK_FROM_HOME = "work_from_home"
    HOLIDAY = "holiday"


class AttendanceSource(str, Enum):
    MANUAL = "manual"
    BIOMETRIC = "biometric"
    MOBILE = "mobile"
    WEB = "web"
    DEVICE = "device"


class AttendanceRecordStatus(str, Enum):
    RECORDED = "recorded"
    ADJUSTED = "adjusted"
    LOCKED = "locked"


class DocumentType(str, Enum):
    ID_PROOF = "id_proof"
    ADDRESS_PROOF = "address_proof"
    CONTRACT = "contract"
    CERTIFICATE = "certificate"
    OTHER = "other"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ReviewCycle(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"


class PerformanceReviewStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class GoalStatus(str, Enum):
    OPEN = "open"
    ACHIEVED = "achieved"
    MISSED = "missed"
    CANCELLED = "cancelled"


class AppraisalArea(str, Enum):
    GOALS = "goals"
    KPI = "kpi"
    COMPETENCY = "competency"
    BEHAVIOR = "behavior"
    ATTENDANCE = "attendance"


class AppraisalStatus(str, Enum):
    DRAFT = "draft"
    FINAL = "final"


class TrainingType(str, Enum):
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    SOFT_SKILLS = "soft_skills"
    LEADERSHIP = "leadership"


class TrainingStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TrainingAttendanceStatus(str, Enum):
    REGISTERED = "registered"
    ATTENDED = "attended"
    ABSENT = "absent"
    COMPLETED = "completed"


class TrainingAttendanceRecordStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class SeparationType(str, Enum):
    RESIGNATION = "resignation"
    TERMINATION = "termination"
    RETIREMENT = "retirement"


class SeparationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    MANAGER_APPROVED = "manager_approved"
    HR_APPROVED = "hr_approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HrEntityType(str, Enum):
    EMPLOYMENT = "employment"
    LEAVE_REQUEST = "leave_request"
    SHIFT_ASSIGNMENT = "shift_assignment"
    EMPLOYEE_DOCUMENT = "employee_document"
    PERFORMANCE_REVIEW = "performance_review"
    TRAINING = "training"
    SEPARATION = "separation"
    DESIGNATION = "designation"
    SHIFT = "shift"
    LEAVE_TYPE = "leave_type"
    HOLIDAY_CALENDAR = "holiday_calendar"


CODE_PREFIXES: dict[HrEntityType, tuple[str, int]] = {
    HrEntityType.EMPLOYMENT: ("EMPL-", 6),
    HrEntityType.LEAVE_REQUEST: ("LVE-", 6),
    HrEntityType.SHIFT_ASSIGNMENT: ("SFA-", 6),
    HrEntityType.EMPLOYEE_DOCUMENT: ("EDOC-", 6),
    HrEntityType.PERFORMANCE_REVIEW: ("PRF-", 6),
    HrEntityType.TRAINING: ("TRN-", 6),
    HrEntityType.SEPARATION: ("SEP-", 6),
    HrEntityType.DESIGNATION: ("DES-", 6),
    HrEntityType.SHIFT: ("SFT-", 6),
    HrEntityType.LEAVE_TYPE: ("LT-", 6),
    HrEntityType.HOLIDAY_CALENDAR: ("HOL-", 6),
}
''',
)

w(
    HR / "domain" / "exceptions.py",
    '''
"""HR domain exceptions."""

from core.exceptions import ConflictException


class InvalidDesignationState(ConflictException):
    def __init__(self, message: str = "Invalid designation state") -> None:
        super().__init__(message)


class InvalidEmployeeProfileState(ConflictException):
    def __init__(self, message: str = "Invalid employee profile state") -> None:
        super().__init__(message)


class InvalidEmploymentState(ConflictException):
    def __init__(self, message: str = "Invalid employment state") -> None:
        super().__init__(message)


class InvalidAssignmentState(ConflictException):
    def __init__(self, message: str = "Invalid assignment state") -> None:
        super().__init__(message)


class InvalidShiftState(ConflictException):
    def __init__(self, message: str = "Invalid shift state") -> None:
        super().__init__(message)


class InvalidShiftAssignmentState(ConflictException):
    def __init__(self, message: str = "Invalid shift assignment state") -> None:
        super().__init__(message)


class InvalidHolidayCalendarState(ConflictException):
    def __init__(self, message: str = "Invalid holiday calendar state") -> None:
        super().__init__(message)


class InvalidLeaveTypeState(ConflictException):
    def __init__(self, message: str = "Invalid leave type state") -> None:
        super().__init__(message)


class InvalidLeaveBalanceState(ConflictException):
    def __init__(self, message: str = "Invalid leave balance state") -> None:
        super().__init__(message)


class InvalidLeaveRequestState(ConflictException):
    def __init__(self, message: str = "Invalid leave request state") -> None:
        super().__init__(message)


class InvalidAttendanceState(ConflictException):
    def __init__(self, message: str = "Invalid attendance state") -> None:
        super().__init__(message)


class InvalidEmployeeDocumentState(ConflictException):
    def __init__(self, message: str = "Invalid employee document state") -> None:
        super().__init__(message)


class InvalidPerformanceReviewState(ConflictException):
    def __init__(self, message: str = "Invalid performance review state") -> None:
        super().__init__(message)


class InvalidGoalState(ConflictException):
    def __init__(self, message: str = "Invalid goal state") -> None:
        super().__init__(message)


class InvalidAppraisalState(ConflictException):
    def __init__(self, message: str = "Invalid appraisal state") -> None:
        super().__init__(message)


class InvalidTrainingState(ConflictException):
    def __init__(self, message: str = "Invalid training state") -> None:
        super().__init__(message)


class InvalidTrainingAttendanceState(ConflictException):
    def __init__(self, message: str = "Invalid training attendance state") -> None:
        super().__init__(message)


class InvalidSeparationState(ConflictException):
    def __init__(self, message: str = "Invalid separation state") -> None:
        super().__init__(message)


class HrIdentitySyncError(ConflictException):
    def __init__(self, message: str = "HR identity sync failed") -> None:
        super().__init__(message)
''',
)

w(
    HR / "domain" / "value_objects.py",
    '''
"""HR value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LeaveDays:
    value: Decimal

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Leave days must be positive")


@dataclass(frozen=True)
class RatingScore:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1 or self.value > 5:
            raise ValueError("Rating must be 1-5")
''',
)

w(
    HR / "domain" / "entities.py",
    '''
"""HR domain entity markers (aggregates map 1:1 to ORM headers)."""

from enum import Enum


class HrAggregate(str, Enum):
    DESIGNATION = "hr_designation"
    EMPLOYEE_PROFILE = "hr_employee_profile"
    EMPLOYMENT = "hr_employment"
    DEPARTMENT_ASSIGNMENT = "hr_department_assignment"
    DESIGNATION_ASSIGNMENT = "hr_designation_assignment"
    SHIFT = "hr_shift"
    SHIFT_ASSIGNMENT = "hr_shift_assignment"
    HOLIDAY_CALENDAR = "hr_holiday_calendar"
    LEAVE_TYPE = "hr_leave_type"
    LEAVE_BALANCE = "hr_leave_balance"
    LEAVE_REQUEST = "hr_leave_request"
    ATTENDANCE = "hr_attendance"
    EMPLOYEE_DOCUMENT = "hr_employee_document"
    PERFORMANCE_REVIEW = "hr_performance_review"
    GOAL = "hr_goal"
    APPRAISAL = "hr_appraisal"
    TRAINING = "hr_training"
    TRAINING_ATTENDANCE = "hr_training_attendance"
    SEPARATION = "hr_separation"
''',
)

print("domain done")
