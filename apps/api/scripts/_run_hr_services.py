"""Write HR service layer files from _gen_hr_services constants."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HR = ROOT / "src" / "modules" / "hr"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def load_mod():
    spec = importlib.util.spec_from_file_location("gen_hr_services", ROOT / "scripts" / "_gen_hr_services.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main() -> None:
    mod = load_mod()
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

    mapping = [
        ("designation_service.py", mod.DESIGNATION_SERVICE),
        ("employee_profile_service.py", mod.PROFILE_SERVICE),
        ("employment_service.py", mod.EMPLOYMENT_SERVICE),
        ("assignment_service.py", mod.ASSIGNMENT_SERVICE),
        ("shift_service.py", mod.SHIFT_SERVICE),
        ("holiday_calendar_service.py", mod.HOLIDAY_SERVICE),
        ("leave_service.py", mod.LEAVE_SERVICE),
        ("attendance_service.py", mod.ATTENDANCE_SERVICE),
        ("document_service.py", mod.DOCUMENT_SERVICE),
        ("performance_service.py", mod.PERFORMANCE_SERVICE),
        ("training_service.py", mod.TRAINING_SERVICE),
        ("separation_service.py", mod.SEPARATION_SERVICE),
        ("report_service.py", mod.REPORT_SERVICE),
        ("integration_service.py", mod.INTEGRATION_SERVICE),
        ("application_service.py", mod.APPLICATION_SERVICE),
    ]
    for fname, content in mapping:
        w(HR / "service" / fname, content)

    w(HR / "permissions.py", mod.PERMISSIONS)
    w(HR / "dependencies.py", mod.DEPENDENCIES)
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
    print("OK services")


if __name__ == "__main__":
    main()
