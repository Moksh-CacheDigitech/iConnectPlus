"""Write HR schemas, routers, tasks, seeds, tests, and wiring."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HR = ROOT / "src" / "modules" / "hr"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = ROOT / "src" / "tests"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def patch_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        print("skip", path.relative_to(ROOT))
        return
    if old not in text:
        raise SystemExit(f"marker missing in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("patched", path.relative_to(ROOT))


def main() -> None:
    w(HR / "schemas.py", SCHEMAS)
    w(HR / "routers" / "__init__.py", ROUTERS)
    w(HR / "router.py", ROUTER)
    w(HR / "tasks.py", TASKS)
    w(ALEMBIC / "0177_seed_hr_permissions.py", SEED_PERMS)
    w(ALEMBIC / "0178_seed_hr_workflows.py", SEED_WF)
    w(TESTS / "unit" / "hr" / "test_hr_engines.py", TEST_ENGINES)
    w(TESTS / "unit" / "hr" / "test_hr_tasks.py", TEST_TASKS)
    w(TESTS / "security" / "hr" / "test_hr_permissions.py", TEST_PERMS)
    w(TESTS / "integration" / "hr" / "test_hr_module_import.py", TEST_IMPORT)

    patch_file(
        ROOT / "src" / "shared" / "router.py",
        "from modules.crm.router import crm_router\n",
        "from modules.crm.router import crm_router\nfrom modules.hr.router import hr_router\n",
    )
    patch_file(
        ROOT / "src" / "shared" / "router.py",
        "api_v1_router.include_router(crm_router)\n",
        "api_v1_router.include_router(crm_router)\napi_v1_router.include_router(hr_router)\n",
    )
    patch_file(
        ROOT / "alembic" / "env.py",
        "import modules.crm.models  # noqa: F401 — register ORM metadata\n",
        "import modules.crm.models  # noqa: F401 — register ORM metadata\n"
        "import modules.hr.models  # noqa: F401 — register ORM metadata\n",
    )
    patch_file(
        ROOT / "src" / "workers" / "celery_app.py",
        '        "modules.crm",\n',
        '        "modules.crm",\n        "modules.hr",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '    "modules.crm.*",\n',
        '    "modules.crm.*",\n    "modules.hr.*",\n',
    )
    print("OK rest+wiring")


SCHEMAS = r'''"""HR Pydantic schemas."""

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DesignationCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID | None = None
    designation_code: str
    designation_name: str
    job_level: str | None = None
    status: str = "active"


class DesignationUpdate(BaseModel):
    designation_name: str | None = None
    job_level: str | None = None
    status: str | None = None
    version: int | None = None


class DesignationResponse(OrmModel):
    id: UUID
    company_id: UUID
    designation_code: str
    designation_name: str
    job_level: str | None
    status: str
    version: int


class EmployeeProfileCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    date_of_birth: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    nationality: str | None = None
    blood_group: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_mobile: str | None = None
    permanent_address_json: dict | None = None
    current_address_json: dict | None = None
    status: str = "active"


class EmployeeProfileUpdate(BaseModel):
    date_of_birth: date | None = None
    gender: str | None = None
    marital_status: str | None = None
    nationality: str | None = None
    blood_group: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_mobile: str | None = None
    permanent_address_json: dict | None = None
    current_address_json: dict | None = None
    status: str | None = None
    version: int | None = None


class EmployeeProfileResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    employee_id: UUID
    status: str
    version: int


class EmploymentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    employment_type: str
    date_of_joining: date
    probation_end_date: date | None = None
    confirmation_date: date | None = None
    contract_end_date: date | None = None
    notice_period_days: int | None = None
    ctc_amount: Decimal | None = None
    currency_code: str | None = None
    work_location_text: str | None = None
    status: str = "draft"


class EmploymentUpdate(BaseModel):
    employment_type: str | None = None
    probation_end_date: date | None = None
    confirmation_date: date | None = None
    contract_end_date: date | None = None
    notice_period_days: int | None = None
    ctc_amount: Decimal | None = None
    currency_code: str | None = None
    work_location_text: str | None = None
    status: str | None = None
    version: int | None = None


class EmploymentResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    employee_id: UUID
    employment_type: str
    date_of_joining: date
    status: str
    version: int


class DepartmentAssignmentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    department_id: UUID
    effective_from: date
    effective_to: date | None = None
    is_primary: bool = True
    assigned_by_employee_id: UUID | None = None
    status: str = "active"


class DepartmentAssignmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    employee_id: UUID
    department_id: UUID
    effective_from: date
    effective_to: date | None
    is_primary: bool
    status: str
    version: int


class DesignationAssignmentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    designation_id: UUID
    effective_from: date
    effective_to: date | None = None
    is_primary: bool = True
    sync_master_label: bool = True
    status: str = "active"


class DesignationAssignmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    employee_id: UUID
    designation_id: UUID
    effective_from: date
    effective_to: date | None
    is_primary: bool
    status: str
    version: int


class ShiftCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID | None = None
    shift_code: str
    shift_name: str
    shift_type: str
    start_time: time
    end_time: time
    grace_minutes: int = 0
    break_minutes: int | None = None
    is_overnight: bool = False
    status: str = "active"


class ShiftUpdate(BaseModel):
    shift_name: str | None = None
    shift_type: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    grace_minutes: int | None = None
    break_minutes: int | None = None
    is_overnight: bool | None = None
    status: str | None = None
    version: int | None = None


class ShiftResponse(OrmModel):
    id: UUID
    company_id: UUID
    shift_code: str
    shift_name: str
    shift_type: str
    start_time: time
    end_time: time
    status: str
    version: int


class ShiftAssignmentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    shift_id: UUID
    effective_from: date
    effective_to: date | None = None


class ShiftAssignmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    employee_id: UUID
    shift_id: UUID
    effective_from: date
    status: str
    version: int


class HolidayCalendarCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID | None = None
    calendar_code: str
    calendar_name: str
    calendar_year: int
    holidays_json: list | dict | None = None
    status: str = "draft"


class HolidayCalendarUpdate(BaseModel):
    calendar_name: str | None = None
    holidays_json: list | dict | None = None
    status: str | None = None
    version: int | None = None


class HolidayCalendarResponse(OrmModel):
    id: UUID
    company_id: UUID
    calendar_code: str
    calendar_name: str
    calendar_year: int
    status: str
    version: int


class LeaveTypeCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID | None = None
    leave_type_code: str
    leave_type_name: str
    is_paid: bool = True
    max_days_per_year: Decimal | None = None
    requires_attachment: bool = False
    status: str = "active"


class LeaveTypeUpdate(BaseModel):
    leave_type_name: str | None = None
    is_paid: bool | None = None
    max_days_per_year: Decimal | None = None
    requires_attachment: bool | None = None
    status: str | None = None
    version: int | None = None


class LeaveTypeResponse(OrmModel):
    id: UUID
    company_id: UUID
    leave_type_code: str
    leave_type_name: str
    is_paid: bool
    status: str
    version: int


class LeaveBalanceCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    leave_type_id: UUID
    balance_year: int
    opening_balance: Decimal = Decimal("0")
    accrued: Decimal = Decimal("0")
    used: Decimal = Decimal("0")
    status: str = "open"


class LeaveBalanceResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    employee_id: UUID
    leave_type_id: UUID
    balance_year: int
    opening_balance: Decimal
    accrued: Decimal
    used: Decimal
    closing_balance: Decimal
    status: str
    version: int


class LeaveRequestCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    leave_type_id: UUID
    start_date: date
    end_date: date
    days_count: Decimal
    reason: str | None = None


class LeaveApproveRequest(BaseModel):
    approver_employee_id: UUID | None = None


class LeaveRequestResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    employee_id: UUID
    leave_type_id: UUID
    start_date: date
    end_date: date
    days_count: Decimal
    status: str
    version: int


class AttendanceCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    attendance_date: date
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None
    total_hours: Decimal | None = None
    attendance_status: str
    source: str = "manual"
    shift_id: UUID | None = None
    notes: str | None = None


class AttendanceUpdate(BaseModel):
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None
    total_hours: Decimal | None = None
    attendance_status: str | None = None
    notes: str | None = None
    version: int | None = None


class AttendanceResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    employee_id: UUID
    attendance_date: date
    attendance_status: str
    source: str
    status: str
    version: int


class EmployeeDocumentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    document_type: str
    document_name: str
    storage_uri: str
    issued_on: date | None = None
    expires_on: date | None = None


class EmployeeDocumentResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    employee_id: UUID
    document_type: str
    document_name: str
    storage_uri: str
    verification_status: str
    status: str
    version: int


class PerformanceReviewCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    reviewer_employee_id: UUID
    review_cycle: str
    period_start: date
    period_end: date
    overall_rating: int | None = None


class PerformanceReviewResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    employee_id: UUID
    reviewer_employee_id: UUID
    review_cycle: str
    period_start: date
    period_end: date
    status: str
    version: int


class GoalCreate(BaseModel):
    company_id: UUID | None = None
    performance_review_id: UUID
    employee_id: UUID | None = None
    sequence_no: int
    goal_title: str
    goal_description: str | None = None
    target_value: Decimal | None = None
    actual_value: Decimal | None = None
    weight_percent: Decimal | None = None


class GoalResponse(OrmModel):
    id: UUID
    performance_review_id: UUID
    employee_id: UUID
    sequence_no: int
    goal_title: str
    status: str
    version: int


class AppraisalCreate(BaseModel):
    company_id: UUID | None = None
    performance_review_id: UUID
    employee_id: UUID | None = None
    sequence_no: int
    appraisal_area: str
    rating: int
    comments: str | None = None


class AppraisalResponse(OrmModel):
    id: UUID
    performance_review_id: UUID
    employee_id: UUID
    sequence_no: int
    appraisal_area: str
    rating: int
    status: str
    version: int


class TrainingCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID | None = None
    training_code: str | None = None
    training_name: str
    training_type: str
    trainer_name: str | None = None
    trainer_employee_id: UUID | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str = "planned"


class TrainingUpdate(BaseModel):
    training_name: str | None = None
    training_type: str | None = None
    trainer_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None
    version: int | None = None


class TrainingResponse(OrmModel):
    id: UUID
    company_id: UUID
    training_code: str
    training_name: str
    training_type: str
    status: str
    version: int


class TrainingAssignRequest(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID


class TrainingAttendanceResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    training_id: UUID
    employee_id: UUID
    attendance_status: str
    status: str
    version: int


class SeparationCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    employee_id: UUID
    separation_type: str
    requested_last_working_date: date
    reason: str | None = None
    clearance_json: dict | None = None


class SeparationApproveRequest(BaseModel):
    stage: str = "manager"


class SeparationCompleteRequest(BaseModel):
    approved_last_working_date: date | None = None


class SeparationResponse(OrmModel):
    id: UUID
    company_id: UUID
    branch_id: UUID
    document_number: str
    employee_id: UUID
    separation_type: str
    requested_last_working_date: date
    approved_last_working_date: date | None
    status: str
    version: int


class ReportSummaryResponse(BaseModel):
    company_id: UUID
    attendance_count: int
    leave_request_count: int
    approved_leave_count: int
    separation_count: int
    completed_separation_count: int
'''

ROUTERS = r'''"""HR REST routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.hr.dependencies import PaginationParams, extract_update_fields, get_pagination, paginate
from modules.hr.schemas import (
    AppraisalCreate,
    AppraisalResponse,
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
    DepartmentAssignmentCreate,
    DepartmentAssignmentResponse,
    DesignationAssignmentCreate,
    DesignationAssignmentResponse,
    DesignationCreate,
    DesignationResponse,
    DesignationUpdate,
    EmployeeDocumentCreate,
    EmployeeDocumentResponse,
    EmployeeProfileCreate,
    EmployeeProfileResponse,
    EmployeeProfileUpdate,
    EmploymentCreate,
    EmploymentResponse,
    EmploymentUpdate,
    GoalCreate,
    GoalResponse,
    HolidayCalendarCreate,
    HolidayCalendarResponse,
    HolidayCalendarUpdate,
    LeaveApproveRequest,
    LeaveBalanceCreate,
    LeaveBalanceResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    LeaveTypeCreate,
    LeaveTypeResponse,
    LeaveTypeUpdate,
    PerformanceReviewCreate,
    PerformanceReviewResponse,
    ReportSummaryResponse,
    SeparationApproveRequest,
    SeparationCompleteRequest,
    SeparationCreate,
    SeparationResponse,
    ShiftAssignmentCreate,
    ShiftAssignmentResponse,
    ShiftCreate,
    ShiftResponse,
    ShiftUpdate,
    TrainingAssignRequest,
    TrainingAttendanceResponse,
    TrainingCreate,
    TrainingResponse,
    TrainingUpdate,
)
from modules.hr.service import (
    AppraisalService,
    AttendanceService,
    DepartmentAssignmentService,
    DesignationAssignmentService,
    DesignationService,
    EmployeeDocumentService,
    EmployeeProfileService,
    EmploymentService,
    GoalService,
    HolidayCalendarService,
    HRReportService,
    LeaveBalanceService,
    LeaveRequestService,
    LeaveTypeService,
    PerformanceService,
    SeparationService,
    ShiftAssignmentService,
    ShiftService,
    TrainingAttendanceService,
    TrainingService,
)
from shared.schemas import APIResponse

designations_router = APIRouter(prefix="/designations", tags=["HR - Designations"])
employee_profiles_router = APIRouter(prefix="/employee-profiles", tags=["HR - Employee Profiles"])
employment_router = APIRouter(prefix="/employment", tags=["HR - Employment"])
department_assignments_router = APIRouter(prefix="/department-assignments", tags=["HR - Department Assignments"])
designation_assignments_router = APIRouter(prefix="/designation-assignments", tags=["HR - Designation Assignments"])
shifts_router = APIRouter(prefix="/shifts", tags=["HR - Shifts"])
shift_assignments_router = APIRouter(prefix="/shift-assignments", tags=["HR - Shift Assignments"])
holiday_calendars_router = APIRouter(prefix="/holiday-calendars", tags=["HR - Holiday Calendars"])
leave_types_router = APIRouter(prefix="/leave-types", tags=["HR - Leave Types"])
leave_balances_router = APIRouter(prefix="/leave-balances", tags=["HR - Leave Balances"])
leave_requests_router = APIRouter(prefix="/leave-requests", tags=["HR - Leave Requests"])
attendance_router = APIRouter(prefix="/attendance", tags=["HR - Attendance"])
employee_documents_router = APIRouter(prefix="/employee-documents", tags=["HR - Employee Documents"])
performance_reviews_router = APIRouter(prefix="/performance-reviews", tags=["HR - Performance Reviews"])
goals_router = APIRouter(prefix="/goals", tags=["HR - Goals"])
appraisals_router = APIRouter(prefix="/appraisals", tags=["HR - Appraisals"])
training_router = APIRouter(prefix="/training", tags=["HR - Training"])
training_attendance_router = APIRouter(prefix="/training-attendance", tags=["HR - Training Attendance"])
separation_router = APIRouter(prefix="/separation", tags=["HR - Separation"])
reports_router = APIRouter(prefix="/reports", tags=["HR - Reports"])


@designations_router.get("", response_model=APIResponse[list[DesignationResponse]])
def list_designations(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.designation:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(DesignationService(db).list(ctx, company_id), pagination))


@designations_router.post("", response_model=APIResponse[DesignationResponse])
def create_designation(
    body: DesignationCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.designation:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=DesignationService(db).create(ctx, **body.model_dump()))


@designations_router.patch("/{row_id}", response_model=APIResponse[DesignationResponse])
def update_designation(
    row_id: UUID,
    body: DesignationUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.designation:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=DesignationService(db).update(ctx, row_id, **extract_update_fields(body)))


@employee_profiles_router.get("", response_model=APIResponse[list[EmployeeProfileResponse]])
def list_profiles(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employee_profile:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(EmployeeProfileService(db).list(ctx, company_id), pagination))


@employee_profiles_router.post("", response_model=APIResponse[EmployeeProfileResponse])
def create_profile(
    body: EmployeeProfileCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employee_profile:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=EmployeeProfileService(db).create(ctx, **body.model_dump()))


@employee_profiles_router.patch("/{row_id}", response_model=APIResponse[EmployeeProfileResponse])
def update_profile(
    row_id: UUID,
    body: EmployeeProfileUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employee_profile:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=EmployeeProfileService(db).update(ctx, row_id, **extract_update_fields(body)))


@employment_router.get("", response_model=APIResponse[list[EmploymentResponse]])
def list_employment(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employment:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(EmploymentService(db).list(ctx, company_id), pagination))


@employment_router.post("", response_model=APIResponse[EmploymentResponse])
def create_employment(
    body: EmploymentCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employment:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=EmploymentService(db).create(ctx, **body.model_dump()))


@employment_router.patch("/{row_id}", response_model=APIResponse[EmploymentResponse])
def update_employment(
    row_id: UUID,
    body: EmploymentUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employment:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=EmploymentService(db).update(ctx, row_id, **extract_update_fields(body)))


@department_assignments_router.get("", response_model=APIResponse[list[DepartmentAssignmentResponse]])
def list_dept_asg(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employment:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(DepartmentAssignmentService(db).list(ctx, company_id), pagination))


@department_assignments_router.post("", response_model=APIResponse[DepartmentAssignmentResponse])
def create_dept_asg(
    body: DepartmentAssignmentCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employment:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=DepartmentAssignmentService(db).create(ctx, **body.model_dump()))


@designation_assignments_router.get("", response_model=APIResponse[list[DesignationAssignmentResponse]])
def list_desig_asg(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employment:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(DesignationAssignmentService(db).list(ctx, company_id), pagination))


@designation_assignments_router.post("", response_model=APIResponse[DesignationAssignmentResponse])
def create_desig_asg(
    body: DesignationAssignmentCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.employment:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=DesignationAssignmentService(db).create(ctx, **body.model_dump()))


@shifts_router.get("", response_model=APIResponse[list[ShiftResponse]])
def list_shifts(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.shift:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(ShiftService(db).list(ctx, company_id), pagination))


@shifts_router.post("", response_model=APIResponse[ShiftResponse])
def create_shift(
    body: ShiftCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.shift:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ShiftService(db).create(ctx, **body.model_dump()))


@shifts_router.patch("/{row_id}", response_model=APIResponse[ShiftResponse])
def update_shift(
    row_id: UUID,
    body: ShiftUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.shift:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ShiftService(db).update(ctx, row_id, **extract_update_fields(body)))


@shift_assignments_router.get("", response_model=APIResponse[list[ShiftAssignmentResponse]])
def list_sfa(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.shift_assignment:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(ShiftAssignmentService(db).list(ctx, company_id), pagination))


@shift_assignments_router.post("", response_model=APIResponse[ShiftAssignmentResponse])
def create_sfa(
    body: ShiftAssignmentCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.shift_assignment:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ShiftAssignmentService(db).create(ctx, **body.model_dump()))


@shift_assignments_router.post("/{row_id}/submit", response_model=APIResponse[ShiftAssignmentResponse])
def submit_sfa(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.shift_assignment:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ShiftAssignmentService(db).submit(ctx, row_id))


@shift_assignments_router.post("/{row_id}/approve", response_model=APIResponse[ShiftAssignmentResponse])
def approve_sfa(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.shift_assignment:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ShiftAssignmentService(db).approve(ctx, row_id))


@holiday_calendars_router.get("", response_model=APIResponse[list[HolidayCalendarResponse]])
def list_holidays(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.holiday_calendar:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(HolidayCalendarService(db).list(ctx, company_id), pagination))


@holiday_calendars_router.post("", response_model=APIResponse[HolidayCalendarResponse])
def create_holiday(
    body: HolidayCalendarCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.holiday_calendar:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=HolidayCalendarService(db).create(ctx, **body.model_dump()))


@holiday_calendars_router.patch("/{row_id}", response_model=APIResponse[HolidayCalendarResponse])
def update_holiday(
    row_id: UUID,
    body: HolidayCalendarUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.holiday_calendar:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=HolidayCalendarService(db).update(ctx, row_id, **extract_update_fields(body)))


@holiday_calendars_router.post("/{row_id}/publish", response_model=APIResponse[HolidayCalendarResponse])
def publish_holiday(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.holiday_calendar:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=HolidayCalendarService(db).publish(ctx, row_id))


@leave_types_router.get("", response_model=APIResponse[list[LeaveTypeResponse]])
def list_leave_types(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave_type:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(LeaveTypeService(db).list(ctx, company_id), pagination))


@leave_types_router.post("", response_model=APIResponse[LeaveTypeResponse])
def create_leave_type(
    body: LeaveTypeCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave_type:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=LeaveTypeService(db).create(ctx, **body.model_dump()))


@leave_types_router.patch("/{row_id}", response_model=APIResponse[LeaveTypeResponse])
def update_leave_type(
    row_id: UUID,
    body: LeaveTypeUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave_type:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=LeaveTypeService(db).update(ctx, row_id, **extract_update_fields(body)))


@leave_balances_router.get("", response_model=APIResponse[list[LeaveBalanceResponse]])
def list_balances(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(LeaveBalanceService(db).list(ctx, company_id), pagination))


@leave_balances_router.post("", response_model=APIResponse[LeaveBalanceResponse])
def create_balance(
    body: LeaveBalanceCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=LeaveBalanceService(db).create(ctx, **body.model_dump()))


@leave_requests_router.get("", response_model=APIResponse[list[LeaveRequestResponse]])
def list_leave_requests(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(LeaveRequestService(db).list(ctx, company_id), pagination))


@leave_requests_router.post("", response_model=APIResponse[LeaveRequestResponse])
def create_leave_request(
    body: LeaveRequestCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=LeaveRequestService(db).create(ctx, **body.model_dump()))


@leave_requests_router.post("/{row_id}/submit", response_model=APIResponse[LeaveRequestResponse])
def submit_leave(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=LeaveRequestService(db).submit(ctx, row_id))


@leave_requests_router.post("/{row_id}/approve", response_model=APIResponse[LeaveRequestResponse])
def approve_leave(
    row_id: UUID,
    body: LeaveApproveRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.leave:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=LeaveRequestService(db).approve(ctx, row_id, **body.model_dump()))


@attendance_router.get("", response_model=APIResponse[list[AttendanceResponse]])
def list_attendance(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.attendance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(AttendanceService(db).list(ctx, company_id), pagination))


@attendance_router.post("", response_model=APIResponse[AttendanceResponse])
def create_attendance(
    body: AttendanceCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.attendance:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AttendanceService(db).create(ctx, **body.model_dump()))


@attendance_router.patch("/{row_id}", response_model=APIResponse[AttendanceResponse])
def update_attendance(
    row_id: UUID,
    body: AttendanceUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.attendance:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AttendanceService(db).update(ctx, row_id, **extract_update_fields(body)))


@attendance_router.post("/{row_id}/lock", response_model=APIResponse[AttendanceResponse])
def lock_attendance(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.attendance:lock"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AttendanceService(db).lock(ctx, row_id))


@employee_documents_router.get("", response_model=APIResponse[list[EmployeeDocumentResponse]])
def list_docs(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.document:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(EmployeeDocumentService(db).list(ctx, company_id), pagination))


@employee_documents_router.post("", response_model=APIResponse[EmployeeDocumentResponse])
def create_doc(
    body: EmployeeDocumentCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.document:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=EmployeeDocumentService(db).create(ctx, **body.model_dump()))


@employee_documents_router.post("/{row_id}/verify", response_model=APIResponse[EmployeeDocumentResponse])
def verify_doc(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.document:verify"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=EmployeeDocumentService(db).verify(ctx, row_id))


@performance_reviews_router.get("", response_model=APIResponse[list[PerformanceReviewResponse]])
def list_reviews(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.performance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(PerformanceService(db).list(ctx, company_id), pagination))


@performance_reviews_router.post("", response_model=APIResponse[PerformanceReviewResponse])
def create_review(
    body: PerformanceReviewCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.performance:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=PerformanceService(db).create(ctx, **body.model_dump()))


@performance_reviews_router.post("/{row_id}/submit", response_model=APIResponse[PerformanceReviewResponse])
def submit_review(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.performance:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=PerformanceService(db).submit(ctx, row_id))


@performance_reviews_router.post("/{row_id}/approve", response_model=APIResponse[PerformanceReviewResponse])
def approve_review(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.performance:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=PerformanceService(db).approve(ctx, row_id))


@goals_router.get("", response_model=APIResponse[list[GoalResponse]])
def list_goals(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.performance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(GoalService(db).list(ctx, company_id), pagination))


@goals_router.post("", response_model=APIResponse[GoalResponse])
def create_goal(
    body: GoalCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.performance:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=GoalService(db).create(ctx, **body.model_dump()))


@appraisals_router.get("", response_model=APIResponse[list[AppraisalResponse]])
def list_appraisals(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.performance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(AppraisalService(db).list(ctx, company_id), pagination))


@appraisals_router.post("", response_model=APIResponse[AppraisalResponse])
def create_appraisal(
    body: AppraisalCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.performance:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AppraisalService(db).create(ctx, **body.model_dump()))


@training_router.get("", response_model=APIResponse[list[TrainingResponse]])
def list_training(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.training:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(TrainingService(db).list(ctx, company_id), pagination))


@training_router.post("", response_model=APIResponse[TrainingResponse])
def create_training(
    body: TrainingCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.training:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=TrainingService(db).create(ctx, **body.model_dump(exclude_none=True)))


@training_router.patch("/{row_id}", response_model=APIResponse[TrainingResponse])
def update_training(
    row_id: UUID,
    body: TrainingUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.training:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=TrainingService(db).update(ctx, row_id, **extract_update_fields(body)))


@training_router.post("/{row_id}/assign", response_model=APIResponse[TrainingAttendanceResponse])
def assign_training(
    row_id: UUID,
    body: TrainingAssignRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.training:assign"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=TrainingService(db).assign(ctx, row_id, **body.model_dump()))


@training_attendance_router.get("", response_model=APIResponse[list[TrainingAttendanceResponse]])
def list_training_attendance(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.training:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(TrainingAttendanceService(db).list(ctx, company_id), pagination))


@separation_router.get("", response_model=APIResponse[list[SeparationResponse]])
def list_separation(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.separation:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=paginate(SeparationService(db).list(ctx, company_id), pagination))


@separation_router.post("", response_model=APIResponse[SeparationResponse])
def create_separation(
    body: SeparationCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.separation:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=SeparationService(db).create(ctx, **body.model_dump()))


@separation_router.post("/{row_id}/submit", response_model=APIResponse[SeparationResponse])
def submit_separation(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.separation:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=SeparationService(db).submit(ctx, row_id))


@separation_router.post("/{row_id}/approve", response_model=APIResponse[SeparationResponse])
def approve_separation(
    row_id: UUID,
    body: SeparationApproveRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.separation:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=SeparationService(db).approve(ctx, row_id, **body.model_dump()))


@separation_router.post("/{row_id}/complete", response_model=APIResponse[SeparationResponse])
def complete_separation(
    row_id: UUID,
    body: SeparationCompleteRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("hr.separation:complete"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=SeparationService(db).complete(ctx, row_id, **body.model_dump()))


@reports_router.get("/summary", response_model=APIResponse[ReportSummaryResponse])
def report_summary(
    ctx: Annotated[TenantContext, Depends(require_permission("hr.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=HRReportService(db).summary(ctx, company_id))
'''

ROUTER = r'''"""HR module router aggregation."""

from fastapi import APIRouter

from modules.hr.routers import (
    appraisals_router,
    attendance_router,
    department_assignments_router,
    designation_assignments_router,
    designations_router,
    employee_documents_router,
    employee_profiles_router,
    employment_router,
    goals_router,
    holiday_calendars_router,
    leave_balances_router,
    leave_requests_router,
    leave_types_router,
    performance_reviews_router,
    reports_router,
    separation_router,
    shift_assignments_router,
    shifts_router,
    training_attendance_router,
    training_router,
)

hr_router = APIRouter(prefix="/hr")
hr_router.include_router(designations_router)
hr_router.include_router(employee_profiles_router)
hr_router.include_router(employment_router)
hr_router.include_router(department_assignments_router)
hr_router.include_router(designation_assignments_router)
hr_router.include_router(shifts_router)
hr_router.include_router(shift_assignments_router)
hr_router.include_router(holiday_calendars_router)
hr_router.include_router(leave_types_router)
hr_router.include_router(leave_balances_router)
hr_router.include_router(leave_requests_router)
hr_router.include_router(attendance_router)
hr_router.include_router(employee_documents_router)
hr_router.include_router(performance_reviews_router)
hr_router.include_router(goals_router)
hr_router.include_router(appraisals_router)
hr_router.include_router(training_router)
hr_router.include_router(training_attendance_router)
hr_router.include_router(separation_router)
hr_router.include_router(reports_router)
'''

TASKS = r'''"""HR Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="hr.attendance_auto_lock")
def attendance_auto_lock() -> dict:
    from datetime import date, timedelta

    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.hr.models import HrAttendance

    db = SessionLocal()
    try:
        cutoff = date.today() - timedelta(days=1)
        rows = list(
            db.scalars(
                select(HrAttendance).where(
                    HrAttendance.is_deleted.is_(False),
                    HrAttendance.status.in_(["recorded", "adjusted"]),
                    HrAttendance.attendance_date <= cutoff,
                )
            ).all()
        )
        return {"status": "ok", "candidates": len(rows)}
    finally:
        db.close()


@celery_app.task(name="hr.leave_balance_accrual")
def leave_balance_accrual() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.hr.models import HrLeaveBalance

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(HrLeaveBalance).where(
                    HrLeaveBalance.is_deleted.is_(False),
                    HrLeaveBalance.status == "open",
                )
            ).all()
        )
        return {"status": "ok", "open_balances": len(rows)}
    finally:
        db.close()


@celery_app.task(name="hr.leave_reminders")
def leave_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.hr.models import HrLeaveRequest

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(HrLeaveRequest).where(
                    HrLeaveRequest.is_deleted.is_(False),
                    HrLeaveRequest.status == "submitted",
                )
            ).all()
        )
        return {"status": "ok", "pending_approvals": len(rows)}
    finally:
        db.close()


@celery_app.task(name="hr.performance_review_due")
def performance_review_due() -> dict:
    from datetime import date

    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.hr.models import HrPerformanceReview

    db = SessionLocal()
    try:
        today = date.today()
        rows = list(
            db.scalars(
                select(HrPerformanceReview).where(
                    HrPerformanceReview.is_deleted.is_(False),
                    HrPerformanceReview.status.in_(["draft", "in_progress"]),
                    HrPerformanceReview.period_end <= today,
                )
            ).all()
        )
        return {"status": "ok", "due_reviews": len(rows)}
    finally:
        db.close()


@celery_app.task(name="hr.training_due_alerts")
def training_due_alerts() -> dict:
    from datetime import date

    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.hr.models import HrTraining

    db = SessionLocal()
    try:
        today = date.today()
        rows = list(
            db.scalars(
                select(HrTraining).where(
                    HrTraining.is_deleted.is_(False),
                    HrTraining.status == "planned",
                    HrTraining.start_date.is_not(None),
                    HrTraining.start_date <= today,
                )
            ).all()
        )
        return {"status": "ok", "due_trainings": len(rows)}
    finally:
        db.close()


@celery_app.task(name="hr.separation_followups")
def separation_followups() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.hr.models import HrSeparation

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(HrSeparation).where(
                    HrSeparation.is_deleted.is_(False),
                    HrSeparation.status.in_(["submitted", "manager_approved", "hr_approved"]),
                )
            ).all()
        )
        return {"status": "ok", "open_separations": len(rows)}
    finally:
        db.close()
'''

SEED_PERMS = r'''"""Seed HR permissions and roles."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.hr.permissions import (
    HR_ADMIN_PERMISSIONS,
    HR_EMPLOYEE_PERMISSIONS,
    HR_EXECUTIVE_PERMISSIONS,
    HR_MANAGER_PERMISSIONS,
    HR_PERMISSIONS,
)

revision: str = "0177_seed_hr_permissions"
down_revision: str | None = "0176_hr_separation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PERMISSION_TABLE = sa.table(
    "sec_permission",
    sa.column("id", sa.Uuid),
    sa.column("permission_code", sa.String),
    sa.column("resource", sa.String),
    sa.column("action", sa.String),
    sa.column("module", sa.String),
    sa.column("is_active", sa.Boolean),
    sa.column("created_at", sa.DateTime(timezone=True)),
    schema="foundation",
)

ROLE_SPECS: list[tuple[str, str, list[str]]] = [
    ("HR_EMPLOYEE", "HR Employee", HR_EMPLOYEE_PERMISSIONS),
    ("HR_MANAGER", "HR Manager", HR_MANAGER_PERMISSIONS),
    ("HR_EXECUTIVE", "HR Executive", HR_EXECUTIVE_PERMISSIONS),
    ("HR_ADMIN", "HR Admin", HR_ADMIN_PERMISSIONS),
]


def _ensure_permission(conn, now, code, resource, action, module):
    exists = conn.execute(
        sa.text("SELECT id FROM foundation.sec_permission WHERE permission_code = :code"),
        {"code": code},
    ).first()
    if exists:
        return str(exists[0])
    perm_id = str(uuid4())
    conn.execute(
        sa.insert(PERMISSION_TABLE).values(
            id=perm_id,
            permission_code=code,
            resource=resource,
            action=action,
            module=module,
            is_active=True,
            created_at=now,
        )
    )
    return perm_id


def _ensure_role(conn, now, tenant_id, role_code, role_name):
    exists = conn.execute(
        sa.text(
            """
            SELECT id FROM foundation.sec_role
            WHERE tenant_id = :tid AND role_code = :code AND is_deleted = false
            """
        ),
        {"tid": tenant_id, "code": role_code},
    ).first()
    if exists:
        return str(exists[0])
    role_id = str(uuid4())
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role
            (id, tenant_id, role_code, role_name, is_system_role, status,
             created_at, updated_at, is_deleted, version)
            VALUES (:id, :tid, :code, :name, true, 'active', :now, :now, false, 1)
            """
        ),
        {"id": role_id, "tid": tenant_id, "code": role_code, "name": role_name, "now": now},
    )
    return role_id


def _grant(conn, now, tenant_id, role_id, perm_id):
    exists = conn.execute(
        sa.text(
            """
            SELECT 1 FROM foundation.sec_role_permission
            WHERE role_id = :rid AND permission_id = :pid
            """
        ),
        {"rid": role_id, "pid": perm_id},
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            """
            INSERT INTO foundation.sec_role_permission
            (id, tenant_id, role_id, permission_id, granted_at)
            VALUES (:id, :tid, :rid, :pid, :now)
            """
        ),
        {"id": str(uuid4()), "tid": tenant_id, "rid": role_id, "pid": perm_id, "now": now},
    )


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    perm_ids: dict[str, str] = {}
    for code, resource, action, module in HR_PERMISSIONS:
        perm_ids[code] = _ensure_permission(conn, now, code, resource, action, module)

    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for role_code, role_name, codes in ROLE_SPECS:
            role_id = _ensure_role(conn, now, tid, role_code, role_name)
            for code in codes:
                _grant(conn, now, tid, role_id, perm_ids[code])


def downgrade() -> None:
    conn = op.get_bind()
    for role_code, _, _ in ROLE_SPECS:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.sec_role_permission WHERE role_id IN (
                  SELECT id FROM foundation.sec_role WHERE role_code = :c
                )
                """
            ),
            {"c": role_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.sec_role WHERE role_code = :c AND is_system_role = true"),
            {"c": role_code},
        )
    for code, _, _, _ in HR_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :c"),
            {"c": code},
        )
'''

SEED_WF = r'''"""Seed HR workflow definitions per ERD_11."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0178_seed_hr_workflows"
down_revision: str | None = "0177_seed_hr_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "HR_LEAVE_APPROVAL",
        "Leave Request Approval",
        "hr_leave_request",
        [
            (1, "HR_EMPLOYEE", "Employee Submit", "role"),
            (2, "HR_MANAGER", "Reporting Manager Approval", "role"),
        ],
    ),
    (
        "HR_SHIFT_CHANGE",
        "Shift Change Approval",
        "hr_shift_assignment",
        [
            (1, "HR_EMPLOYEE", "Employee Submit", "role"),
            (2, "HR_MANAGER", "Manager Approval", "role"),
            (3, "HR_EXECUTIVE", "HR Approval", "role"),
        ],
    ),
    (
        "HR_SEPARATION_APPROVAL",
        "Separation Approval",
        "hr_separation",
        [
            (1, "HR_EMPLOYEE", "Employee Submit", "role"),
            (2, "HR_MANAGER", "Manager Approval", "role"),
            (3, "HR_EXECUTIVE", "HR Approval", "role"),
        ],
    ),
    (
        "HR_PERFORMANCE_APPROVAL",
        "Performance Review Approval",
        "hr_performance_review",
        [
            (1, "HR_MANAGER", "Reviewer Submit", "role"),
            (2, "HR_EXECUTIVE", "HR Approval", "role"),
        ],
    ),
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()

    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for workflow_code, workflow_name, document_type, steps in WORKFLOWS:
            exists = conn.execute(
                sa.text(
                    """
                    SELECT id FROM foundation.wf_definition
                    WHERE tenant_id = :tid AND workflow_code = :code AND version_no = 1
                    """
                ),
                {"tid": tid, "code": workflow_code},
            ).first()
            if exists:
                wf_id = str(exists[0])
            else:
                wf_id = str(uuid4())
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_definition
                        (id, tenant_id, workflow_code, workflow_name, module,
                         document_type, version_no, is_active, created_at, updated_at)
                        VALUES (:id, :tid, :code, :name, 'hr', :doc, 1, true, :now, :now)
                        """
                    ),
                    {
                        "id": wf_id,
                        "tid": tid,
                        "code": workflow_code,
                        "name": workflow_name,
                        "doc": document_type,
                        "now": now,
                    },
                )
            for step_order, step_code, step_name, approver_type in steps:
                step_exists = conn.execute(
                    sa.text(
                        """
                        SELECT 1 FROM foundation.wf_step
                        WHERE workflow_id = :wf AND step_order = :ord
                        """
                    ),
                    {"wf": wf_id, "ord": step_order},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, workflow_id, step_order, step_code, step_name,
                         approver_type, is_parallel, created_at, updated_at)
                        VALUES (:id, :tid, :wf, :ord, :scode, :sname, :atype, false, :now, :now)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wf": wf_id,
                        "ord": step_order,
                        "scode": step_code,
                        "sname": step_name,
                        "atype": approver_type,
                        "now": now,
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    for workflow_code, _, _, _ in WORKFLOWS:
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.wf_step WHERE workflow_id IN (
                  SELECT id FROM foundation.wf_definition WHERE workflow_code = :c
                )
                """
            ),
            {"c": workflow_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.wf_definition WHERE workflow_code = :c"),
            {"c": workflow_code},
        )
'''

TEST_ENGINES = r'''"""Unit tests for HR engines."""

from types import SimpleNamespace
from decimal import Decimal

from modules.hr.service.engines import (
    AttendanceEngine,
    EmploymentEngine,
    LeaveBalanceEngine,
    LeaveRequestEngine,
    SeparationEngine,
)


def test_leave_request_lifecycle():
    engine = LeaveRequestEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"


def test_employment_activate_and_end():
    engine = EmploymentEngine()
    row = SimpleNamespace(status="draft")
    engine.apply_activate(row)
    assert row.status == "active"
    engine.apply_end(row)
    assert row.status == "ended"


def test_separation_flow():
    engine = SeparationEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.manager_approve(row)
    engine.hr_approve(row)
    engine.complete(row)
    assert row.status == "completed"


def test_attendance_lock():
    engine = AttendanceEngine()
    row = SimpleNamespace(status="recorded")
    engine.lock(row)
    assert row.status == "locked"


def test_leave_balance_usage():
    engine = LeaveBalanceEngine()
    row = SimpleNamespace(status="open", opening_balance=Decimal("10"), accrued=Decimal("0"), used=Decimal("0"), closing_balance=Decimal("10"))
    engine.apply_usage(row, Decimal("2"))
    assert row.used == Decimal("2")
    assert row.closing_balance == Decimal("8")
'''

TEST_TASKS = r'''"""Unit tests for HR Celery task registration."""

from modules.hr import tasks


def test_hr_tasks_registered():
    assert callable(tasks.attendance_auto_lock)
    assert callable(tasks.leave_balance_accrual)
    assert callable(tasks.leave_reminders)
    assert callable(tasks.performance_review_due)
    assert callable(tasks.training_due_alerts)
    assert callable(tasks.separation_followups)
'''

TEST_PERMS = r'''"""Security tests for HR permissions/roles."""

from modules.hr.permissions import (
    HR_ADMIN_PERMISSIONS,
    HR_EMPLOYEE_PERMISSIONS,
    HR_EXECUTIVE_PERMISSIONS,
    HR_MANAGER_PERMISSIONS,
    HR_PERMISSIONS,
)


def test_permission_codes_unique():
    codes = [p[0] for p in HR_PERMISSIONS]
    assert len(codes) == len(set(codes))
    assert all(c.startswith("hr.") for c in codes)


def test_roles_have_permissions():
    assert "hr.leave:approve" in HR_MANAGER_PERMISSIONS
    assert "hr.leave:approve" not in HR_EMPLOYEE_PERMISSIONS
    assert "hr.employment:create" in HR_EXECUTIVE_PERMISSIONS
    assert len(HR_ADMIN_PERMISSIONS) == len(HR_PERMISSIONS)
'''

TEST_IMPORT = r'''"""Integration smoke: HR module imports and router mount."""

from modules.hr.models import HrAttendance, HrEmployment, HrLeaveRequest, HrSeparation
from modules.hr.router import hr_router
from modules.hr.service import EmploymentService, HRApplicationService, LeaveService, SeparationService
from modules.hr.service.engines import EmploymentEngine, LeaveRequestEngine, SeparationEngine


def test_hr_models_importable():
    assert HrEmployment.__tablename__ == "hr_employment"
    assert HrLeaveRequest.__tablename__ == "hr_leave_request"
    assert HrAttendance.__tablename__ == "hr_attendance"
    assert HrSeparation.__tablename__ == "hr_separation"


def test_hr_router_mounted():
    assert hr_router.prefix == "/hr"
    assert len(hr_router.routes) > 20


def test_hr_services_and_engines_importable():
    assert EmploymentService is not None
    assert LeaveService is not None
    assert SeparationService is not None
    assert HRApplicationService is not None
    assert EmploymentEngine is not None
    assert LeaveRequestEngine is not None
    assert SeparationEngine is not None
'''


if __name__ == "__main__":
    main()
