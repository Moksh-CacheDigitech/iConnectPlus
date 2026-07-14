"""Generate HR repos, engines, services, adapters, permissions, tasks, seeds, wiring helpers."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HR = ROOT / "src" / "modules" / "hr"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = ROOT / "src" / "tests"

TABLES = [
    ("designation", "HrDesignation", "Designation", True),
    ("employee_profile", "HrEmployeeProfile", "EmployeeProfile", True),
    ("employment", "HrEmployment", "Employment", True),
    ("department_assignment", "HrDepartmentAssignment", "DepartmentAssignment", True),
    ("designation_assignment", "HrDesignationAssignment", "DesignationAssignment", True),
    ("shift", "HrShift", "Shift", False),
    ("shift_assignment", "HrShiftAssignment", "ShiftAssignment", True),
    ("holiday_calendar", "HrHolidayCalendar", "HolidayCalendar", False),
    ("leave_type", "HrLeaveType", "LeaveType", False),
    ("leave_balance", "HrLeaveBalance", "LeaveBalance", True),
    ("leave_request", "HrLeaveRequest", "LeaveRequest", True),
    ("attendance", "HrAttendance", "Attendance", True),
    ("employee_document", "HrEmployeeDocument", "EmployeeDocument", True),
    ("performance_review", "HrPerformanceReview", "PerformanceReview", True),
    ("goal", "HrGoal", "Goal", True),
    ("appraisal", "HrAppraisal", "Appraisal", True),
    ("training", "HrTraining", "Training", False),
    ("training_attendance", "HrTrainingAttendance", "TrainingAttendance", True),
    ("separation", "HrSeparation", "Separation", True),
]


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def repo_template(module: str, cls: str, name: str, branch: bool) -> str:
    list_name = name.replace(" ", "")
    return f'''"""HR {cls} repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.hr.models import {cls}
from modules.hr.repository.base import HrScopedRepository, utcnow
from modules.foundation.domain.value_objects import TenantContext


class {name}Repository(HrScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls} | None:
        stmt = select({cls}).where({cls}.id == row_id, {cls}.is_deleted.is_(False))
        stmt = self.apply_hr_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select({cls}).where(
            {cls}.company_id == company_id,
            {cls}.is_deleted.is_(False),
        )
        stmt = self.apply_hr_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return list(self.db.scalars(stmt).all())

    def create(self, ctx: TenantContext, **fields) -> {cls}:
        row = {cls}(
            id=uuid4(),
            tenant_id=ctx.tenant_id,
            created_by=ctx.user_id,
            updated_by=ctx.user_id,
            **fields,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields) -> {cls} | None:
        row = self.get(ctx, row_id)
        if row is None:
            return None
        for k, v in fields.items():
            if v is not None:
                setattr(row, k, v)
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        if hasattr(row, "version"):
            row.version = int(row.version or 1) + 1
        self.db.flush()
        return row
'''


ENGINE_BODIES = {
    "Designation": '''
class DesignationEngine:
    def validate_active(self, row) -> None:
        if row.status not in {"active", "inactive"}:
            raise InvalidDesignationState("Invalid designation status")

    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "EmployeeProfile": '''
class EmployeeProfileEngine:
    def validate_writable(self, row) -> None:
        if row.status == ActiveInactive.INACTIVE.value:
            raise InvalidEmployeeProfileState("Inactive profile cannot be updated for ESS changes")
''',
    "Employment": '''
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
    "DepartmentAssignment": '''
class DepartmentAssignmentEngine:
    def end(self, row) -> None:
        if row.status != AssignmentStatus.ACTIVE.value:
            raise InvalidAssignmentState("Only active assignments can end")
        row.status = AssignmentStatus.ENDED.value
''',
    "DesignationAssignment": '''
class DesignationAssignmentEngine:
    def end(self, row) -> None:
        if row.status != AssignmentStatus.ACTIVE.value:
            raise InvalidAssignmentState("Only active assignments can end")
        row.status = AssignmentStatus.ENDED.value
''',
    "Shift": '''
class ShiftEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "ShiftAssignment": '''
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
    "HolidayCalendar": '''
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
    "LeaveType": '''
class LeaveTypeEngine:
    def deactivate(self, row) -> None:
        row.status = ActiveInactive.INACTIVE.value
''',
    "LeaveBalance": '''
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
            Decimal(str(row.opening_balance or 0)) + Decimal(str(row.accrued or 0)) - Decimal(str(row.used or 0))
        )
''',
    "LeaveRequest": '''
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
    "Attendance": '''
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
    "EmployeeDocument": '''
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
    "PerformanceReview": '''
class PerformanceReviewEngine:
    def start(self, row) -> None:
        if row.status != PerformanceReviewStatus.DRAFT.value:
            raise InvalidPerformanceReviewState("Only draft reviews can start")
        row.status = PerformanceReviewStatus.IN_PROGRESS.value

    def submit(self, row) -> None:
        if row.status not in {PerformanceReviewStatus.DRAFT.value, PerformanceReviewStatus.IN_PROGRESS.value}:
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
    "Goal": '''
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
    "Appraisal": '''
class AppraisalEngine:
    def finalize(self, row) -> None:
        if row.status != AppraisalStatus.DRAFT.value:
            raise InvalidAppraisalState("Only draft appraisals can be finalized")
        row.status = AppraisalStatus.FINAL.value
''',
    "Training": '''
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
    "TrainingAttendance": '''
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
    "Separation": '''
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

ENGINE_IMPORTS = '''
from decimal import Decimal

from modules.hr.domain.enums import (
    ActiveInactive,
    AppraisalStatus,
    AssignmentStatus,
    AttendanceRecordStatus,
    DocumentStatus,
    EmploymentStatus,
    GoalStatus,
    HolidayCalendarStatus,
    LeaveBalanceStatus,
    LeaveRequestStatus,
    PerformanceReviewStatus,
    SeparationStatus,
    ShiftAssignmentStatus,
    TrainingAttendanceRecordStatus,
    TrainingAttendanceStatus,
    TrainingStatus,
    VerificationStatus,
)
from modules.hr.domain.exceptions import (
    InvalidAppraisalState,
    InvalidAssignmentState,
    InvalidAttendanceState,
    InvalidDesignationState,
    InvalidEmployeeDocumentState,
    InvalidEmployeeProfileState,
    InvalidEmploymentState,
    InvalidGoalState,
    InvalidHolidayCalendarState,
    InvalidLeaveBalanceState,
    InvalidLeaveRequestState,
    InvalidPerformanceReviewState,
    InvalidSeparationState,
    InvalidShiftAssignmentState,
    InvalidTrainingAttendanceState,
    InvalidTrainingState,
)
'''


def main() -> None:
    w(
        HR / "repository" / "base.py",
        '''"""HR repository base utilities."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HrScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_hr_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = HrScopedRepository.apply_tenant_filter(stmt, model, ctx)
        if ctx.company_id and ctx.user_type not in {"super_admin", "tenant_admin"}:
            stmt = stmt.where(model.company_id == ctx.company_id)
        if (
            branch_scoped
            and ctx.branch_id
            and ctx.user_type not in {"super_admin", "tenant_admin"}
            and hasattr(model, "branch_id")
        ):
            stmt = stmt.where(model.branch_id == ctx.branch_id)
        return stmt

    @staticmethod
    def resolve_company_id(ctx: TenantContext, company_id: UUID | None) -> UUID:
        if company_id is not None:
            HrScopedRepository.ensure_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
''',
    )

    w(
        HR / "repository" / "code_sequence_repository.py",
        '''"""HR document code sequences."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.hr.domain.enums import CODE_PREFIXES, HrEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: HrEntityType, company_id: UUID, model, code_column: str) -> str:
        prefix, width = CODE_PREFIXES[entity]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-"
        stmt = select(getattr(model, code_column)).where(
            model.company_id == company_id,
            getattr(model, code_column).like(f"{full_prefix}%"),
            model.is_deleted.is_(False),
        )
        existing = list(self.db.scalars(stmt).all())
        seq = 1
        if existing:
            nums = []
            for code in existing:
                try:
                    nums.append(int(str(code).rsplit("-", 1)[-1]))
                except ValueError:
                    continue
            if nums:
                seq = max(nums) + 1
        return f"{full_prefix}{seq:0{width}d}"
''',
    )

    for module, cls, name, branch in TABLES:
        w(HR / "repository" / f"{module}_repository.py", repo_template(module, cls, name, branch))

    # Engines
    for name, body in ENGINE_BODIES.items():
        # camel to snake for filename
        snake = "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_")
        # Fix known names
        snake_map = {
            "Designation": "designation",
            "EmployeeProfile": "employee_profile",
            "Employment": "employment",
            "DepartmentAssignment": "department_assignment",
            "DesignationAssignment": "designation_assignment",
            "Shift": "shift",
            "ShiftAssignment": "shift_assignment",
            "HolidayCalendar": "holiday_calendar",
            "LeaveType": "leave_type",
            "LeaveBalance": "leave_balance",
            "LeaveRequest": "leave_request",
            "Attendance": "attendance",
            "EmployeeDocument": "employee_document",
            "PerformanceReview": "performance_review",
            "Goal": "goal",
            "Appraisal": "appraisal",
            "Training": "training",
            "TrainingAttendance": "training_attendance",
            "Separation": "separation",
        }
        fname = snake_map[name]
        w(
            HR / "service" / "engines" / f"{fname}_engine.py",
            f'"""{name} lifecycle engine."""\n{ENGINE_IMPORTS}\n{body}\n',
        )

    engine_exports = "\n".join(
        f"from modules.hr.service.engines.{''.join(['_' + c.lower() if c.isupper() else c for c in n]).lstrip('_') if False else {'Designation':'designation','EmployeeProfile':'employee_profile','Employment':'employment','DepartmentAssignment':'department_assignment','DesignationAssignment':'designation_assignment','Shift':'shift','ShiftAssignment':'shift_assignment','HolidayCalendar':'holiday_calendar','LeaveType':'leave_type','LeaveBalance':'leave_balance','LeaveRequest':'leave_request','Attendance':'attendance','EmployeeDocument':'employee_document','PerformanceReview':'performance_review','Goal':'goal','Appraisal':'appraisal','Training':'training','TrainingAttendance':'training_attendance','Separation':'separation'}[n]}_engine import {n}Engine"
        for n in ENGINE_BODIES
    )
    # simpler write
    lines = []
    all_names = []
    for n in ENGINE_BODIES:
        fname = {
            "Designation": "designation",
            "EmployeeProfile": "employee_profile",
            "Employment": "employment",
            "DepartmentAssignment": "department_assignment",
            "DesignationAssignment": "designation_assignment",
            "Shift": "shift",
            "ShiftAssignment": "shift_assignment",
            "HolidayCalendar": "holiday_calendar",
            "LeaveType": "leave_type",
            "LeaveBalance": "leave_balance",
            "LeaveRequest": "leave_request",
            "Attendance": "attendance",
            "EmployeeDocument": "employee_document",
            "PerformanceReview": "performance_review",
            "Goal": "goal",
            "Appraisal": "appraisal",
            "Training": "training",
            "TrainingAttendance": "training_attendance",
            "Separation": "separation",
        }[n]
        lines.append(f"from modules.hr.service.engines.{fname}_engine import {n}Engine")
        all_names.append(f'"{n}Engine"')
    w(
        HR / "service" / "engines" / "__init__.py",
        '"""HR business engines."""\n\n'
        + "\n".join(lines)
        + "\n\n__all__ = [\n    "
        + ",\n    ".join(all_names)
        + ",\n]\n",
    )

    print("repos + engines done")


if __name__ == "__main__":
    main()
