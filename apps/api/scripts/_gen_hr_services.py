"""Generate HR services, adapters, permissions, seeds, APIs, tasks, tests, wiring."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HR = ROOT / "src" / "modules" / "hr"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = ROOT / "src" / "tests"
SHARED = ROOT / "src" / "shared"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def patch_file(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new.strip() in text:
        print("skip (already)", path.relative_to(ROOT))
        return
    if old not in text:
        raise SystemExit(f"patch failed in {path}: marker not found")
    path.write_text(text.replace(old, new), encoding="utf-8")
    print("patched", path.relative_to(ROOT))


def main() -> None:
    # Scope + document numbering
    w(
        HR / "service" / "hr_scope_validator.py",
        '''"""HR scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.hr.repository.base import HrScopedRepository


class HrScopeValidator(HrScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id)
''',
    )
    w(
        HR / "service" / "document_number_service.py",
        '''"""HR document numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.hr.domain.enums import HrEntityType
from modules.hr.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: HrEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
''',
    )

    # Adapters
    w(
        HR / "adapters" / "master_data_port.py",
        '''"""Master Data port — HR never ORM-writes master_* tables."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.domain.enums import EmployeeStatus
from modules.master_data.service.employee_service import EmployeeService


class HrMasterDataAdapter:
    def __init__(self, db: Session) -> None:
        self._employees = EmployeeService(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._employees.get_employee(ctx, employee_id)

    def sync_designation_label(self, ctx: TenantContext, employee_id: UUID, designation: str):
        return self._employees.update_employee(ctx, employee_id, designation=designation)

    def complete_separation_identity(
        self,
        ctx: TenantContext,
        employee_id: UUID,
        *,
        separation_type: str,
        date_of_leaving: date,
    ):
        status = EmployeeStatus.RESIGNED.value
        if separation_type == "termination":
            status = EmployeeStatus.TERMINATED.value
        elif separation_type == "retirement":
            status = EmployeeStatus.RESIGNED.value
        return self._employees.update_employee(
            ctx,
            employee_id,
            status=status,
            date_of_leaving=date_of_leaving,
        )
''',
    )
    w(
        HR / "adapters" / "organization_port.py",
        '''"""Organization port — read org_department only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.hierarchy_repository import DepartmentRepository


class HrOrganizationAdapter:
    def __init__(self, db: Session) -> None:
        self._departments = DepartmentRepository(db)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        department = self._departments.get_by_id(ctx, department_id)
        if department is None:
            raise NotFoundException("Department not found")
        return department
''',
    )
    w(
        HR / "adapters" / "__init__.py",
        '''"""HR adapters."""

from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.adapters.organization_port import HrOrganizationAdapter

__all__ = ["HrMasterDataAdapter", "HrOrganizationAdapter"]
''',
    )

    # Core services — write a comprehensive services file set
    w(HR / "service" / "designation_service.py", DESIGNATION_SERVICE)
    w(HR / "service" / "employee_profile_service.py", PROFILE_SERVICE)
    w(HR / "service" / "employment_service.py", EMPLOYMENT_SERVICE)
    w(HR / "service" / "assignment_service.py", ASSIGNMENT_SERVICE)
    w(HR / "service" / "shift_service.py", SHIFT_SERVICE)
    w(HR / "service" / "holiday_calendar_service.py", HOLIDAY_SERVICE)
    w(HR / "service" / "leave_service.py", LEAVE_SERVICE)
    w(HR / "service" / "attendance_service.py", ATTENDANCE_SERVICE)
    w(HR / "service" / "document_service.py", DOCUMENT_SERVICE)
    w(HR / "service" / "performance_service.py", PERFORMANCE_SERVICE)
    w(HR / "service" / "training_service.py", TRAINING_SERVICE)
    w(HR / "service" / "separation_service.py", SEPARATION_SERVICE)
    w(HR / "service" / "report_service.py", REPORT_SERVICE)
    w(HR / "service" / "integration_service.py", INTEGRATION_SERVICE)
    w(HR / "service" / "application_service.py", APPLICATION_SERVICE)
    w(
        HR / "service" / "__init__.py",
        '''"""HR services."""

from modules.hr.service.application_service import HRApplicationService
from modules.hr.service.assignment_service import (
    DepartmentAssignmentService,
    DesignationAssignmentService,
)
from modules.hr.service.attendance_service import AttendanceService
from modules.hr.service.designation_service import DesignationService
from modules.hr.service.document_service import EmployeeDocumentService
from modules.hr.service.employee_profile_service import EmployeeProfileService
from modules.hr.service.employment_service import EmploymentService
from modules.hr.service.holiday_calendar_service import HolidayCalendarService
from modules.hr.service.integration_service import HRIntegrationService
from modules.hr.service.leave_service import LeaveBalanceService, LeaveRequestService, LeaveTypeService
from modules.hr.service.performance_service import AppraisalService, GoalService, PerformanceService
from modules.hr.service.report_service import HRReportService
from modules.hr.service.separation_service import SeparationService
from modules.hr.service.shift_service import ShiftAssignmentService, ShiftService
from modules.hr.service.training_service import TrainingAttendanceService, TrainingService

# Aliases expected by user prompt
LeaveService = LeaveRequestService

__all__ = [
    "AppraisalService",
    "AttendanceService",
    "DepartmentAssignmentService",
    "DesignationAssignmentService",
    "DesignationService",
    "EmployeeDocumentService",
    "EmployeeProfileService",
    "EmploymentService",
    "GoalService",
    "HolidayCalendarService",
    "HRApplicationService",
    "HRIntegrationService",
    "HRReportService",
    "LeaveBalanceService",
    "LeaveRequestService",
    "LeaveService",
    "LeaveTypeService",
    "PerformanceService",
    "SeparationService",
    "ShiftAssignmentService",
    "ShiftService",
    "TrainingAttendanceService",
    "TrainingService",
]
''',
    )

    w(HR / "permissions.py", PERMISSIONS)
    w(HR / "dependencies.py", DEPENDENCIES)
    w(HR / "schemas.py", SCHEMAS)
    w(HR / "routers" / "__init__.py", ROUTERS)
    w(
        HR / "router.py",
        '''"""HR module router aggregation."""

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
''',
    )
    w(HR / "tasks.py", TASKS)
    w(ALEMBIC / "0177_seed_hr_permissions.py", SEED_PERMS)
    w(ALEMBIC / "0178_seed_hr_workflows.py", SEED_WF)

    # Tests
    w(TESTS / "unit" / "hr" / "test_hr_engines.py", TEST_ENGINES)
    w(TESTS / "unit" / "hr" / "test_hr_tasks.py", TEST_TASKS)
    w(TESTS / "security" / "hr" / "test_hr_permissions.py", TEST_PERMS)
    w(TESTS / "integration" / "hr" / "test_hr_module_import.py", TEST_IMPORT)

    # Wiring
    patch_file(
        SHARED / "router.py",
        "from modules.crm.router import crm_router\n",
        "from modules.crm.router import crm_router\nfrom modules.hr.router import hr_router\n",
    )
    patch_file(
        SHARED / "router.py",
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

    print("services/apis/seeds/wiring done")


# ===== Large string constants =====

DESIGNATION_SERVICE = '''"""Designation application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.models import HrDesignation
from modules.hr.repository.designation_repository import DesignationRepository
from modules.hr.service.engines import DesignationEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class DesignationService:
    def __init__(self, db: Session) -> None:
        self._repo = DesignationRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = DesignationEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> HrDesignation:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Designation not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        row = self._repo.create(ctx, company_id=cid, **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_designation",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Designation not found")
        return row
'''

PROFILE_SERVICE = '''"""Employee profile application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.repository.employee_profile_repository import EmployeeProfileRepository
from modules.hr.service.engines import EmployeeProfileEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class EmployeeProfileService:
    def __init__(self, db: Session) -> None:
        self._repo = EmployeeProfileRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = EmployeeProfileEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Employee profile not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        row = self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            **fields,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_employee_profile",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        row = self.get(ctx, row_id)
        self._engine.validate_writable(row)
        updated = self._repo.update(ctx, row_id, **fields)
        if updated is None:
            raise NotFoundException("Employee profile not found")
        return updated
'''

EMPLOYMENT_SERVICE = '''"""Employment application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import EmploymentStatus, HrEntityType
from modules.hr.models import HrEmployment
from modules.hr.repository.employment_repository import EmploymentRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import EmploymentEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class EmploymentService:
    def __init__(self, db: Session) -> None:
        self._repo = EmploymentRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = EmploymentEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> HrEmployment:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Employment not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        status = fields.get("status", EmploymentStatus.DRAFT.value)
        if status in EmploymentEngine.ACTIVE_SET:
            self._ensure_single_active(ctx, cid, employee_id)
        doc = self._numbers.generate(HrEntityType.EMPLOYMENT, cid, HrEmployment, "document_number")
        row = self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            document_number=doc,
            **fields,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_employment",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Employment not found")
        return row

    def activate(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._ensure_single_active(ctx, row.company_id, row.employee_id, exclude_id=row_id)
        self._engine.apply_activate(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def confirm(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.apply_confirm(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def end(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.apply_end(row)
        updated = self._repo.update(ctx, row_id, status=row.status)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_employment",
            entity_id=row_id,
            operation="end",
            performed_by=ctx.user_id,
        )
        return updated

    def _ensure_single_active(
        self,
        ctx: TenantContext,
        company_id: UUID,
        employee_id: UUID,
        exclude_id: UUID | None = None,
    ) -> None:
        for existing in self._repo.list_rows(ctx, company_id):
            if existing.employee_id != employee_id:
                continue
            if exclude_id and existing.id == exclude_id:
                continue
            if existing.status in EmploymentEngine.ACTIVE_SET:
                raise ConflictException("Employee already has an active employment record")
'''

ASSIGNMENT_SERVICE = '''"""Department / designation assignment services."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.adapters.organization_port import HrOrganizationAdapter
from modules.hr.repository.department_assignment_repository import DepartmentAssignmentRepository
from modules.hr.repository.designation_assignment_repository import DesignationAssignmentRepository
from modules.hr.repository.designation_repository import DesignationRepository
from modules.hr.service.engines import DepartmentAssignmentEngine, DesignationAssignmentEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class DepartmentAssignmentService:
    def __init__(self, db: Session) -> None:
        self._repo = DepartmentAssignmentRepository(db)
        self._scope = HrScopeValidator(db)
        self._org = HrOrganizationAdapter(db)
        self._master = HrMasterDataAdapter(db)
        self._engine = DepartmentAssignmentEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Department assignment not found")
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        employee_id: UUID,
        department_id: UUID,
        effective_from: date,
        company_id: UUID | None = None,
        **fields,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        self._org.get_department(ctx, department_id)
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            department_id=department_id,
            effective_from=effective_from,
            **fields,
        )

    def end(self, ctx: TenantContext, row_id: UUID, *, effective_to: date | None = None):
        row = self.get(ctx, row_id)
        self._engine.end(row)
        return self._repo.update(
            ctx,
            row_id,
            status=row.status,
            effective_to=effective_to or date.today(),
        )


class DesignationAssignmentService:
    def __init__(self, db: Session) -> None:
        self._repo = DesignationAssignmentRepository(db)
        self._designations = DesignationRepository(db)
        self._scope = HrScopeValidator(db)
        self._master = HrMasterDataAdapter(db)
        self._engine = DesignationAssignmentEngine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Designation assignment not found")
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        employee_id: UUID,
        designation_id: UUID,
        effective_from: date,
        company_id: UUID | None = None,
        sync_master_label: bool = True,
        **fields,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        designation = self._designations.get(ctx, designation_id)
        if designation is None:
            raise NotFoundException("Designation not found")
        row = self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            designation_id=designation_id,
            effective_from=effective_from,
            **fields,
        )
        if sync_master_label and fields.get("is_primary", True):
            self._master.sync_designation_label(ctx, employee_id, designation.designation_name)
        return row

    def end(self, ctx: TenantContext, row_id: UUID, *, effective_to: date | None = None):
        row = self.get(ctx, row_id)
        self._engine.end(row)
        return self._repo.update(
            ctx,
            row_id,
            status=row.status,
            effective_to=effective_to or date.today(),
        )
'''

SHIFT_SERVICE = '''"""Shift / shift assignment services."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType, ShiftAssignmentStatus
from modules.hr.models import HrShiftAssignment
from modules.hr.repository.shift_assignment_repository import ShiftAssignmentRepository
from modules.hr.repository.shift_repository import ShiftRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import ShiftAssignmentEngine, ShiftEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class ShiftService:
    def __init__(self, db: Session) -> None:
        self._repo = ShiftRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = ShiftEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Shift not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.create(ctx, company_id=cid, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Shift not found")
        return row


class ShiftAssignmentService:
    def __init__(self, db: Session) -> None:
        self._repo = ShiftAssignmentRepository(db)
        self._shifts = ShiftRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ShiftAssignmentEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Shift assignment not found")
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        employee_id: UUID,
        shift_id: UUID,
        effective_from: date,
        company_id: UUID | None = None,
        **fields,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        if self._shifts.get(ctx, shift_id) is None:
            raise NotFoundException("Shift not found")
        doc = self._numbers.generate(
            HrEntityType.SHIFT_ASSIGNMENT, cid, HrShiftAssignment, "document_number"
        )
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            shift_id=shift_id,
            effective_from=effective_from,
            document_number=doc,
            status=fields.pop("status", ShiftAssignmentStatus.DRAFT.value),
            **fields,
        )

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)
'''

HOLIDAY_SERVICE = '''"""Holiday calendar service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ConflictException, NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.hr.domain.enums import HolidayCalendarStatus
from modules.hr.repository.holiday_calendar_repository import HolidayCalendarRepository
from modules.hr.service.engines import HolidayCalendarEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class HolidayCalendarService:
    def __init__(self, db: Session) -> None:
        self._repo = HolidayCalendarRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = HolidayCalendarEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Holiday calendar not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.create(ctx, company_id=cid, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Holiday calendar not found")
        return row

    def publish(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        for existing in self._repo.list_rows(ctx, row.company_id):
            if (
                existing.id != row.id
                and existing.calendar_year == row.calendar_year
                and existing.status == HolidayCalendarStatus.PUBLISHED.value
            ):
                raise ConflictException("Published holiday calendar already exists for year")
        self._engine.publish(row)
        return self._repo.update(ctx, row_id, status=row.status)
'''

LEAVE_SERVICE = '''"""Leave type / balance / request services."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType, LeaveRequestStatus
from modules.hr.models import HrLeaveRequest
from modules.hr.repository.leave_balance_repository import LeaveBalanceRepository
from modules.hr.repository.leave_request_repository import LeaveRequestRepository
from modules.hr.repository.leave_type_repository import LeaveTypeRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import LeaveBalanceEngine, LeaveRequestEngine, LeaveTypeEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class LeaveTypeService:
    def __init__(self, db: Session) -> None:
        self._repo = LeaveTypeRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = LeaveTypeEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Leave type not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.create(ctx, company_id=cid, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Leave type not found")
        return row


class LeaveBalanceService:
    def __init__(self, db: Session) -> None:
        self._repo = LeaveBalanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._master = HrMasterDataAdapter(db)
        self._engine = LeaveBalanceEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Leave balance not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        opening = Decimal(str(fields.get("opening_balance", 0)))
        accrued = Decimal(str(fields.get("accrued", 0)))
        used = Decimal(str(fields.get("used", 0)))
        fields.setdefault("closing_balance", opening + accrued - used)
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            **fields,
        )


class LeaveRequestService:
    def __init__(self, db: Session) -> None:
        self._repo = LeaveRequestRepository(db)
        self._balances = LeaveBalanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = LeaveRequestEngine()
        self._balance_engine = LeaveBalanceEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Leave request not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        doc = self._numbers.generate(HrEntityType.LEAVE_REQUEST, cid, HrLeaveRequest, "document_number")
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            document_number=doc,
            status=fields.pop("status", LeaveRequestStatus.DRAFT.value),
            **fields,
        )

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID, *, approver_employee_id: UUID | None = None):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        balance = None
        for bal in self._balances.list_rows(ctx, row.company_id):
            if (
                bal.employee_id == row.employee_id
                and bal.leave_type_id == row.leave_type_id
                and bal.balance_year == row.start_date.year
                and bal.status == "open"
            ):
                balance = bal
                break
        if balance is None:
            raise NotFoundException("Open leave balance not found for approval year")
        self._balance_engine.apply_usage(balance, row.days_count)
        self._balances.update(
            ctx,
            balance.id,
            used=balance.used,
            closing_balance=balance.closing_balance,
        )
        updated = self._repo.update(
            ctx,
            row_id,
            status=row.status,
            approver_employee_id=approver_employee_id,
            decided_at=datetime.now(timezone.utc),
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_leave_request",
            entity_id=row_id,
            operation="approve",
            performed_by=ctx.user_id,
        )
        return updated

    def reject(self, ctx: TenantContext, row_id: UUID, *, approver_employee_id: UUID | None = None):
        row = self.get(ctx, row_id)
        self._engine.reject(row)
        return self._repo.update(
            ctx,
            row_id,
            status=row.status,
            approver_employee_id=approver_employee_id,
            decided_at=datetime.now(timezone.utc),
        )
'''

ATTENDANCE_SERVICE = '''"""Attendance service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import AttendanceRecordStatus
from modules.hr.repository.attendance_repository import AttendanceRepository
from modules.hr.service.engines import AttendanceEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class AttendanceService:
    def __init__(self, db: Session) -> None:
        self._repo = AttendanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = AttendanceEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Attendance not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            status=fields.pop("status", AttendanceRecordStatus.RECORDED.value),
            **fields,
        )

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        row = self.get(ctx, row_id)
        if row.status == AttendanceRecordStatus.LOCKED.value:
            self._engine.adjust(row)  # raises
        self._engine.adjust(row)
        return self._repo.update(ctx, row_id, status=AttendanceRecordStatus.ADJUSTED.value, **fields)

    def lock(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.lock(row)
        updated = self._repo.update(ctx, row_id, status=row.status)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_attendance",
            entity_id=row_id,
            operation="lock",
            performed_by=ctx.user_id,
        )
        return updated
'''

DOCUMENT_SERVICE = '''"""Employee document service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType
from modules.hr.models import HrEmployeeDocument
from modules.hr.repository.employee_document_repository import EmployeeDocumentRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import EmployeeDocumentEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class EmployeeDocumentService:
    def __init__(self, db: Session) -> None:
        self._repo = EmployeeDocumentRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = EmployeeDocumentEngine()
        self._master = HrMasterDataAdapter(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Employee document not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        doc = self._numbers.generate(
            HrEntityType.EMPLOYEE_DOCUMENT, cid, HrEmployeeDocument, "document_number"
        )
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            document_number=doc,
            **fields,
        )

    def verify(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.verify(row)
        return self._repo.update(ctx, row_id, verification_status=row.verification_status)
'''

PERFORMANCE_SERVICE = '''"""Performance review / goals / appraisal services."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType
from modules.hr.models import HrPerformanceReview
from modules.hr.repository.appraisal_repository import AppraisalRepository
from modules.hr.repository.goal_repository import GoalRepository
from modules.hr.repository.performance_review_repository import PerformanceReviewRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import AppraisalEngine, GoalEngine, PerformanceReviewEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class PerformanceService:
    def __init__(self, db: Session) -> None:
        self._repo = PerformanceReviewRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = PerformanceReviewEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Performance review not found")
        return row

    def create(
        self,
        ctx: TenantContext,
        *,
        branch_id: UUID,
        employee_id: UUID,
        reviewer_employee_id: UUID,
        company_id: UUID | None = None,
        **fields,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        self._master.get_employee(ctx, reviewer_employee_id)
        doc = self._numbers.generate(
            HrEntityType.PERFORMANCE_REVIEW, cid, HrPerformanceReview, "document_number"
        )
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            reviewer_employee_id=reviewer_employee_id,
            document_number=doc,
            **fields,
        )

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        updated = self._repo.update(ctx, row_id, status=row.status)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_performance_review",
            entity_id=row_id,
            operation="approve",
            performed_by=ctx.user_id,
        )
        return updated


class GoalService:
    def __init__(self, db: Session) -> None:
        self._repo = GoalRepository(db)
        self._reviews = PerformanceReviewRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = GoalEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def create(self, ctx: TenantContext, *, performance_review_id: UUID, company_id: UUID | None = None, **fields):
        review = self._reviews.get(ctx, performance_review_id)
        if review is None:
            raise NotFoundException("Performance review not found")
        cid = self._scope.resolve_company_id(ctx, company_id or review.company_id)
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=review.branch_id,
            performance_review_id=performance_review_id,
            employee_id=fields.pop("employee_id", review.employee_id),
            **fields,
        )


class AppraisalService:
    def __init__(self, db: Session) -> None:
        self._repo = AppraisalRepository(db)
        self._reviews = PerformanceReviewRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = AppraisalEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def create(self, ctx: TenantContext, *, performance_review_id: UUID, company_id: UUID | None = None, **fields):
        review = self._reviews.get(ctx, performance_review_id)
        if review is None:
            raise NotFoundException("Performance review not found")
        cid = self._scope.resolve_company_id(ctx, company_id or review.company_id)
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=review.branch_id,
            performance_review_id=performance_review_id,
            employee_id=fields.pop("employee_id", review.employee_id),
            **fields,
        )

    def finalize(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Appraisal not found")
        self._engine.finalize(row)
        return self._repo.update(ctx, row_id, status=row.status)
'''

TRAINING_SERVICE = '''"""Training services."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType
from modules.hr.models import HrTraining
from modules.hr.repository.training_attendance_repository import TrainingAttendanceRepository
from modules.hr.repository.training_repository import TrainingRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import TrainingAttendanceEngine, TrainingEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class TrainingService:
    def __init__(self, db: Session) -> None:
        self._repo = TrainingRepository(db)
        self._attendance = TrainingAttendanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = TrainingEngine()
        self._master = HrMasterDataAdapter(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Training not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        code = fields.pop("training_code", None) or self._numbers.generate(
            HrEntityType.TRAINING, cid, HrTraining, "training_code"
        )
        return self._repo.create(ctx, company_id=cid, training_code=code, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("Training not found")
        return row

    def assign(
        self,
        ctx: TenantContext,
        training_id: UUID,
        *,
        branch_id: UUID,
        employee_id: UUID,
        company_id: UUID | None = None,
        **fields,
    ):
        training = self.get(ctx, training_id)
        cid = self._scope.resolve_company_id(ctx, company_id or training.company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        return self._attendance.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            training_id=training_id,
            employee_id=employee_id,
            **fields,
        )


class TrainingAttendanceService:
    def __init__(self, db: Session) -> None:
        self._repo = TrainingAttendanceRepository(db)
        self._scope = HrScopeValidator(db)
        self._engine = TrainingAttendanceEngine()

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def mark_attended(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Training attendance not found")
        self._engine.mark_attended(row)
        return self._repo.update(ctx, row_id, attendance_status=row.attendance_status)
'''

SEPARATION_SERVICE = '''"""Separation service — completes via Master Data identity sync."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.domain.enums import HrEntityType
from modules.hr.models import HrSeparation
from modules.hr.repository.separation_repository import SeparationRepository
from modules.hr.service.document_number_service import DocumentNumberService
from modules.hr.service.engines import SeparationEngine
from modules.hr.service.hr_scope_validator import HrScopeValidator


class SeparationService:
    def __init__(self, db: Session) -> None:
        self._repo = SeparationRepository(db)
        self._scope = HrScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = SeparationEngine()
        self._master = HrMasterDataAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID):
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("Separation not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, employee_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        self._master.get_employee(ctx, employee_id)
        doc = self._numbers.generate(HrEntityType.SEPARATION, cid, HrSeparation, "document_number")
        return self._repo.create(
            ctx,
            company_id=cid,
            branch_id=branch_id,
            employee_id=employee_id,
            document_number=doc,
            **fields,
        )

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID, *, stage: str = "manager"):
        row = self.get(ctx, row_id)
        if stage == "manager":
            self._engine.manager_approve(row)
        else:
            self._engine.hr_approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def complete(self, ctx: TenantContext, row_id: UUID, *, approved_last_working_date: date | None = None):
        row = self.get(ctx, row_id)
        self._engine.complete(row)
        lwd = approved_last_working_date or row.approved_last_working_date or row.requested_last_working_date
        updated = self._repo.update(
            ctx,
            row_id,
            status=row.status,
            approved_last_working_date=lwd,
        )
        self._master.complete_separation_identity(
            ctx,
            row.employee_id,
            separation_type=row.separation_type,
            date_of_leaving=lwd,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="hr_separation",
            entity_id=row_id,
            operation="complete",
            performed_by=ctx.user_id,
        )
        return updated
'''

REPORT_SERVICE = '''"""HR report service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.hr.repository.attendance_repository import AttendanceRepository
from modules.hr.repository.leave_request_repository import LeaveRequestRepository
from modules.hr.repository.separation_repository import SeparationRepository
from modules.hr.service.hr_scope_validator import HrScopeValidator


class HRReportService:
    def __init__(self, db: Session) -> None:
        self._scope = HrScopeValidator(db)
        self._attendance = AttendanceRepository(db)
        self._leave = LeaveRequestRepository(db)
        self._separation = SeparationRepository(db)

    def summary(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        attendance = self._attendance.list_rows(ctx, cid)
        leaves = self._leave.list_rows(ctx, cid)
        separations = self._separation.list_rows(ctx, cid)
        return {
            "company_id": cid,
            "attendance_count": len(attendance),
            "leave_request_count": len(leaves),
            "approved_leave_count": sum(1 for r in leaves if r.status == "approved"),
            "separation_count": len(separations),
            "completed_separation_count": sum(1 for r in separations if r.status == "completed"),
        }
'''

INTEGRATION_SERVICE = '''"""HR integration facade — Master Data sync + Payroll-ready read exports."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.hr.adapters.master_data_port import HrMasterDataAdapter
from modules.hr.repository.attendance_repository import AttendanceRepository
from modules.hr.repository.employment_repository import EmploymentRepository
from modules.hr.repository.leave_request_repository import LeaveRequestRepository
from modules.hr.service.hr_scope_validator import HrScopeValidator


class HRIntegrationService:
    """Expose employment / attendance / leave facts for future Payroll. No payroll writes."""

    def __init__(self, db: Session) -> None:
        self._scope = HrScopeValidator(db)
        self._master = HrMasterDataAdapter(db)
        self._employment = EmploymentRepository(db)
        self._attendance = AttendanceRepository(db)
        self._leave = LeaveRequestRepository(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def payroll_employment_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        cid = self._scope.resolve_company_id(ctx, company_id)
        rows = self._employment.list_rows(ctx, cid)
        return [
            {
                "employment_id": r.id,
                "employee_id": r.employee_id,
                "employment_type": r.employment_type,
                "status": r.status,
                "date_of_joining": r.date_of_joining,
                "ctc_amount": r.ctc_amount,
                "currency_code": r.currency_code,
            }
            for r in rows
            if r.status in {"active", "probation", "confirmed"}
        ]

    def payroll_attendance_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        cid = self._scope.resolve_company_id(ctx, company_id)
        return [
            {
                "attendance_id": r.id,
                "employee_id": r.employee_id,
                "attendance_date": r.attendance_date,
                "attendance_status": r.attendance_status,
                "total_hours": r.total_hours,
                "status": r.status,
            }
            for r in self._attendance.list_rows(ctx, cid)
        ]

    def payroll_leave_facts(self, ctx: TenantContext, company_id: UUID | None = None) -> list[dict]:
        cid = self._scope.resolve_company_id(ctx, company_id)
        return [
            {
                "leave_request_id": r.id,
                "employee_id": r.employee_id,
                "leave_type_id": r.leave_type_id,
                "start_date": r.start_date,
                "end_date": r.end_date,
                "days_count": r.days_count,
                "status": r.status,
            }
            for r in self._leave.list_rows(ctx, cid)
            if r.status == "approved"
        ]
'''

APPLICATION_SERVICE = '''"""HR application service facade."""

from sqlalchemy.orm import Session

from modules.hr.service.assignment_service import (
    DepartmentAssignmentService,
    DesignationAssignmentService,
)
from modules.hr.service.attendance_service import AttendanceService
from modules.hr.service.designation_service import DesignationService
from modules.hr.service.document_service import EmployeeDocumentService
from modules.hr.service.employee_profile_service import EmployeeProfileService
from modules.hr.service.employment_service import EmploymentService
from modules.hr.service.holiday_calendar_service import HolidayCalendarService
from modules.hr.service.integration_service import HRIntegrationService
from modules.hr.service.leave_service import LeaveBalanceService, LeaveRequestService, LeaveTypeService
from modules.hr.service.performance_service import AppraisalService, GoalService, PerformanceService
from modules.hr.service.report_service import HRReportService
from modules.hr.service.separation_service import SeparationService
from modules.hr.service.shift_service import ShiftAssignmentService, ShiftService
from modules.hr.service.training_service import TrainingAttendanceService, TrainingService


class HRApplicationService:
    def __init__(self, db: Session) -> None:
        self.designations = DesignationService(db)
        self.employee_profiles = EmployeeProfileService(db)
        self.employment = EmploymentService(db)
        self.department_assignments = DepartmentAssignmentService(db)
        self.designation_assignments = DesignationAssignmentService(db)
        self.shifts = ShiftService(db)
        self.shift_assignments = ShiftAssignmentService(db)
        self.holiday_calendars = HolidayCalendarService(db)
        self.leave_types = LeaveTypeService(db)
        self.leave_balances = LeaveBalanceService(db)
        self.leave_requests = LeaveRequestService(db)
        self.attendance = AttendanceService(db)
        self.documents = EmployeeDocumentService(db)
        self.performance = PerformanceService(db)
        self.goals = GoalService(db)
        self.appraisals = AppraisalService(db)
        self.training = TrainingService(db)
        self.training_attendance = TrainingAttendanceService(db)
        self.separation = SeparationService(db)
        self.reports = HRReportService(db)
        self.integration = HRIntegrationService(db)
'''

# Continue in part 2 of file - permissions, schemas, routers etc. will be appended
# because this file is getting huge. Split remaining into constants at end.

PERMISSIONS = '''"""HR permission constants per ERD_11."""

HR_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("hr.designation:read", "hr.designation", "read", "hr"),
    ("hr.designation:create", "hr.designation", "create", "hr"),
    ("hr.designation:update", "hr.designation", "update", "hr"),
    ("hr.shift:read", "hr.shift", "read", "hr"),
    ("hr.shift:create", "hr.shift", "create", "hr"),
    ("hr.shift:update", "hr.shift", "update", "hr"),
    ("hr.leave_type:read", "hr.leave_type", "read", "hr"),
    ("hr.leave_type:create", "hr.leave_type", "create", "hr"),
    ("hr.leave_type:update", "hr.leave_type", "update", "hr"),
    ("hr.holiday_calendar:read", "hr.holiday_calendar", "read", "hr"),
    ("hr.holiday_calendar:create", "hr.holiday_calendar", "create", "hr"),
    ("hr.holiday_calendar:update", "hr.holiday_calendar", "update", "hr"),
    ("hr.employee_profile:read", "hr.employee_profile", "read", "hr"),
    ("hr.employee_profile:create", "hr.employee_profile", "create", "hr"),
    ("hr.employee_profile:update", "hr.employee_profile", "update", "hr"),
    ("hr.employment:read", "hr.employment", "read", "hr"),
    ("hr.employment:create", "hr.employment", "create", "hr"),
    ("hr.employment:update", "hr.employment", "update", "hr"),
    ("hr.attendance:read", "hr.attendance", "read", "hr"),
    ("hr.attendance:create", "hr.attendance", "create", "hr"),
    ("hr.attendance:update", "hr.attendance", "update", "hr"),
    ("hr.attendance:lock", "hr.attendance", "lock", "hr"),
    ("hr.leave:read", "hr.leave", "read", "hr"),
    ("hr.leave:create", "hr.leave", "create", "hr"),
    ("hr.leave:submit", "hr.leave", "submit", "hr"),
    ("hr.leave:approve", "hr.leave", "approve", "hr"),
    ("hr.shift_assignment:read", "hr.shift_assignment", "read", "hr"),
    ("hr.shift_assignment:create", "hr.shift_assignment", "create", "hr"),
    ("hr.shift_assignment:submit", "hr.shift_assignment", "submit", "hr"),
    ("hr.shift_assignment:approve", "hr.shift_assignment", "approve", "hr"),
    ("hr.document:read", "hr.document", "read", "hr"),
    ("hr.document:create", "hr.document", "create", "hr"),
    ("hr.document:verify", "hr.document", "verify", "hr"),
    ("hr.performance:read", "hr.performance", "read", "hr"),
    ("hr.performance:create", "hr.performance", "create", "hr"),
    ("hr.performance:submit", "hr.performance", "submit", "hr"),
    ("hr.performance:approve", "hr.performance", "approve", "hr"),
    ("hr.training:read", "hr.training", "read", "hr"),
    ("hr.training:create", "hr.training", "create", "hr"),
    ("hr.training:update", "hr.training", "update", "hr"),
    ("hr.training:assign", "hr.training", "assign", "hr"),
    ("hr.separation:read", "hr.separation", "read", "hr"),
    ("hr.separation:create", "hr.separation", "create", "hr"),
    ("hr.separation:submit", "hr.separation", "submit", "hr"),
    ("hr.separation:approve", "hr.separation", "approve", "hr"),
    ("hr.separation:complete", "hr.separation", "complete", "hr"),
    ("hr.report:read", "hr.report", "read", "hr"),
    ("hr.report:export", "hr.report", "export", "hr"),
]

HR_EMPLOYEE_PERMISSIONS = [
    "hr.employee_profile:read",
    "hr.employment:read",
    "hr.attendance:read",
    "hr.leave:read",
    "hr.leave:create",
    "hr.leave:submit",
    "hr.shift_assignment:read",
    "hr.document:read",
    "hr.performance:read",
    "hr.training:read",
    "hr.separation:read",
    "hr.separation:create",
    "hr.separation:submit",
    "hr.holiday_calendar:read",
    "hr.leave_type:read",
    "hr.shift:read",
    "hr.designation:read",
]

HR_MANAGER_PERMISSIONS = list(
    dict.fromkeys(
        HR_EMPLOYEE_PERMISSIONS
        + [
            "hr.leave:approve",
            "hr.shift_assignment:create",
            "hr.shift_assignment:submit",
            "hr.shift_assignment:approve",
            "hr.performance:create",
            "hr.performance:submit",
            "hr.performance:approve",
            "hr.separation:approve",
            "hr.attendance:create",
            "hr.attendance:update",
            "hr.report:read",
        ]
    )
)

HR_EXECUTIVE_PERMISSIONS = list(
    dict.fromkeys(
        HR_MANAGER_PERMISSIONS
        + [
            "hr.designation:create",
            "hr.designation:update",
            "hr.shift:create",
            "hr.shift:update",
            "hr.leave_type:create",
            "hr.leave_type:update",
            "hr.holiday_calendar:create",
            "hr.holiday_calendar:update",
            "hr.employee_profile:create",
            "hr.employee_profile:update",
            "hr.employment:create",
            "hr.employment:update",
            "hr.attendance:lock",
            "hr.document:create",
            "hr.document:verify",
            "hr.training:create",
            "hr.training:update",
            "hr.training:assign",
            "hr.separation:complete",
            "hr.report:export",
        ]
    )
)

HR_ADMIN_PERMISSIONS = [p[0] for p in HR_PERMISSIONS]
'''

DEPENDENCIES = '''"""HR module dependencies."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query

from database.session import get_db
from modules.foundation.dependencies import get_tenant_context, require_permission
from modules.foundation.domain.value_objects import TenantContext

__all__ = [
    "PaginationParams",
    "get_pagination",
    "get_tenant_context",
    "require_permission",
    "TenantContext",
    "get_db",
    "paginate",
    "extract_update_fields",
]


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=200)] = 25,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def paginate(items: list, pagination: PaginationParams) -> list:
    return items[pagination.offset : pagination.offset + pagination.page_size]


def extract_update_fields(body) -> dict:
    fields = body.model_dump(exclude_unset=True)
    fields.pop("version", None)
    return fields
'''

# Placeholder - schemas/routers/tasks/seeds/tests filled in separately if file too large
SCHEMAS = "PLACEHOLDER"
ROUTERS = "PLACEHOLDER"
TASKS = "PLACEHOLDER"
SEED_PERMS = "PLACEHOLDER"
SEED_WF = "PLACEHOLDER"
TEST_ENGINES = "PLACEHOLDER"
TEST_TASKS = "PLACEHOLDER"
TEST_PERMS = "PLACEHOLDER"
TEST_IMPORT = "PLACEHOLDER"

if __name__ == "__main__":
    # Part 1 only creates constants - actual main uses them; we load part2
    print("This module defines generators; run _gen_hr_services_part2.py")
