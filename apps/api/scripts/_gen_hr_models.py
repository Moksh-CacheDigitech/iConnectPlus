"""Generate HR ORM models and alembic table migrations."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HR = ROOT / "src" / "modules" / "hr"
ALEMBIC = ROOT / "alembic" / "versions"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


MODELS: dict[str, str] = {}

MODELS["designation"] = r'''"""HR designation catalog ORM."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrMasterMixin


class HrDesignation(Base, *HrMasterMixin):
    __tablename__ = "hr_designation"
    __table_args__ = (
        UniqueConstraint("company_id", "designation_code", name="uk_hr_desig_company_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_hr_desig_status"),
        CheckConstraint(
            "job_level IS NULL OR job_level IN ('junior','mid','senior','lead','exec')",
            name="ck_hr_desig_job_level",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    designation_code: Mapped[str] = mapped_column(String(50), nullable=False)
    designation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["employee_profile"] = r'''"""HR employee profile ORM — extends master_employee (C-01)."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrEmployeeProfile(Base, *HrTransactionMixin):
    __tablename__ = "hr_employee_profile"
    __table_args__ = (
        UniqueConstraint("employee_id", name="uk_hr_profile_employee"),
        CheckConstraint("status IN ('active','inactive')", name="ck_hr_profile_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(30), nullable=True)
    marital_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_mobile: Mapped[str | None] = mapped_column(String(30), nullable=True)
    permanent_address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    current_address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["employment"] = r'''"""HR employment ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrEmployment(Base, *HrTransactionMixin):
    __tablename__ = "hr_employment"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_hr_empl_company_doc"),
        CheckConstraint(
            "employment_type IN ('permanent','contract','intern','consultant')",
            name="ck_hr_empl_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','probation','confirmed','ended','cancelled')",
            name="ck_hr_empl_status",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=False)
    probation_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    confirmation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    contract_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notice_period_days: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    ctc_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    work_location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["department_assignment"] = r'''"""HR department assignment — uses org_department only (C-01)."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrDepartmentAssignment(Base, *HrTransactionMixin):
    __tablename__ = "hr_department_assignment"
    __table_args__ = (
        CheckConstraint("status IN ('active','ended')", name="ck_hr_dept_asg_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    assigned_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["designation_assignment"] = r'''"""HR designation assignment history."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrDesignationAssignment(Base, *HrTransactionMixin):
    __tablename__ = "hr_designation_assignment"
    __table_args__ = (
        CheckConstraint("status IN ('active','ended')", name="ck_hr_desig_asg_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    designation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_designation.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["shift"] = r'''"""HR shift catalog ORM."""

from datetime import time
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, SmallInteger, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrMasterMixin


class HrShift(Base, *HrMasterMixin):
    __tablename__ = "hr_shift"
    __table_args__ = (
        UniqueConstraint("company_id", "shift_code", name="uk_hr_shift_company_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_hr_shift_status"),
        CheckConstraint(
            "shift_type IN ('general','morning','evening','night','rotational')",
            name="ck_hr_shift_type",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    shift_code: Mapped[str] = mapped_column(String(50), nullable=False)
    shift_name: Mapped[str] = mapped_column(String(255), nullable=False)
    shift_type: Mapped[str] = mapped_column(String(30), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    grace_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    break_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_overnight: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["shift_assignment"] = r'''"""HR shift assignment ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrShiftAssignment(Base, *HrTransactionMixin):
    __tablename__ = "hr_shift_assignment"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_hr_sfa_company_doc"),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','ended','cancelled')",
            name="ck_hr_sfa_status",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    shift_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_shift.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
'''

MODELS["holiday_calendar"] = r'''"""HR holiday calendar ORM."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrMasterMixin


class HrHolidayCalendar(Base, *HrMasterMixin):
    __tablename__ = "hr_holiday_calendar"
    __table_args__ = (
        UniqueConstraint("company_id", "calendar_code", name="uk_hr_hol_company_code"),
        CheckConstraint(
            "status IN ('draft','published','archived')",
            name="ck_hr_hol_status",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    calendar_code: Mapped[str] = mapped_column(String(50), nullable=False)
    calendar_name: Mapped[str] = mapped_column(String(255), nullable=False)
    calendar_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    holidays_json: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["leave_type"] = r'''"""HR leave type catalog ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrMasterMixin


class HrLeaveType(Base, *HrMasterMixin):
    __tablename__ = "hr_leave_type"
    __table_args__ = (
        UniqueConstraint("company_id", "leave_type_code", name="uk_hr_ltype_company_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_hr_ltype_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    leave_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    leave_type_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    max_days_per_year: Mapped[Decimal | None] = mapped_column(Numeric(9, 2), nullable=True)
    requires_attachment: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["leave_balance"] = r'''"""HR leave balance ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrLeaveBalance(Base, *HrTransactionMixin):
    __tablename__ = "hr_leave_balance"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "employee_id",
            "leave_type_id",
            "balance_year",
            name="uk_hr_lbal_emp_type_year",
        ),
        CheckConstraint("status IN ('open','closed')", name="ck_hr_lbal_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    leave_type_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_leave_type.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    balance_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False, default=0)
    accrued: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False, default=0)
    used: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False, default=0)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
'''

MODELS["leave_request"] = r'''"""HR leave request ORM."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrLeaveRequest(Base, *HrTransactionMixin):
    __tablename__ = "hr_leave_request"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_hr_lve_company_doc"),
        CheckConstraint(
            "status IN ('draft','submitted','approved','rejected','cancelled')",
            name="ck_hr_lve_status",
        ),
        CheckConstraint("end_date >= start_date", name="ck_hr_lve_dates"),
        CheckConstraint("days_count > 0", name="ck_hr_lve_days"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    leave_type_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_leave_type.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    days_count: Mapped[Decimal] = mapped_column(Numeric(9, 2), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
    approver_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
'''

MODELS["attendance"] = r'''"""HR attendance ORM."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrAttendance(Base, *HrTransactionMixin):
    __tablename__ = "hr_attendance"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "employee_id",
            "attendance_date",
            name="uk_hr_att_emp_date",
        ),
        CheckConstraint(
            "attendance_status IN ('present','absent','half_day','work_from_home','holiday')",
            name="ck_hr_att_day_status",
        ),
        CheckConstraint(
            "source IN ('manual','biometric','mobile','web','device')",
            name="ck_hr_att_source",
        ),
        CheckConstraint(
            "status IN ('recorded','adjusted','locked')",
            name="ck_hr_att_status",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_hours: Mapped[Decimal | None] = mapped_column(Numeric(9, 2), nullable=True)
    attendance_status: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")
    shift_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_shift.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
'''

MODELS["employee_document"] = r'''"""HR employee document metadata ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrEmployeeDocument(Base, *HrTransactionMixin):
    __tablename__ = "hr_employee_document"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_hr_edoc_company_doc"),
        CheckConstraint(
            "document_type IN ('id_proof','address_proof','contract','certificate','other')",
            name="ck_hr_edoc_type",
        ),
        CheckConstraint(
            "verification_status IN ('pending','verified','rejected')",
            name="ck_hr_edoc_verification",
        ),
        CheckConstraint("status IN ('active','archived')", name="ck_hr_edoc_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    issued_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["performance_review"] = r'''"""HR performance review ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrPerformanceReview(Base, *HrTransactionMixin):
    __tablename__ = "hr_performance_review"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_hr_prf_company_doc"),
        CheckConstraint(
            "review_cycle IN ('monthly','quarterly','half_yearly','yearly')",
            name="ck_hr_prf_cycle",
        ),
        CheckConstraint(
            "status IN ('draft','in_progress','submitted','approved','closed','cancelled')",
            name="ck_hr_prf_status",
        ),
        CheckConstraint(
            "overall_rating IS NULL OR (overall_rating BETWEEN 1 AND 5)",
            name="ck_hr_prf_rating",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reviewer_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    review_cycle: Mapped[str] = mapped_column(String(30), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
    overall_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
'''

MODELS["goal"] = r'''"""HR goal ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrDetailMixin


class HrGoal(Base, *HrDetailMixin):
    __tablename__ = "hr_goal"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open','achieved','missed','cancelled')",
            name="ck_hr_goal_status",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    performance_review_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_performance_review.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    goal_title: Mapped[str] = mapped_column(String(255), nullable=False)
    goal_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    actual_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    weight_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
'''

MODELS["appraisal"] = r'''"""HR appraisal ORM."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrDetailMixin


class HrAppraisal(Base, *HrDetailMixin):
    __tablename__ = "hr_appraisal"
    __table_args__ = (
        CheckConstraint(
            "appraisal_area IN ('goals','kpi','competency','behavior','attendance')",
            name="ck_hr_appr_area",
        ),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_hr_appr_rating"),
        CheckConstraint("status IN ('draft','final')", name="ck_hr_appr_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    performance_review_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_performance_review.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    appraisal_area: Mapped[str] = mapped_column(String(30), nullable=False)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["training"] = r'''"""HR training ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrMasterMixin


class HrTraining(Base, *HrMasterMixin):
    __tablename__ = "hr_training"
    __table_args__ = (
        UniqueConstraint("company_id", "training_code", name="uk_hr_trn_company_code"),
        CheckConstraint(
            "training_type IN ('technical','compliance','soft_skills','leadership')",
            name="ck_hr_trn_type",
        ),
        CheckConstraint(
            "status IN ('planned','in_progress','completed','cancelled')",
            name="ck_hr_trn_status",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    training_code: Mapped[str] = mapped_column(String(50), nullable=False)
    training_name: Mapped[str] = mapped_column(String(255), nullable=False)
    training_type: Mapped[str] = mapped_column(String(30), nullable=False)
    trainer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    trainer_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
'''

MODELS["training_attendance"] = r'''"""HR training attendance ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrTrainingAttendance(Base, *HrTransactionMixin):
    __tablename__ = "hr_training_attendance"
    __table_args__ = (
        UniqueConstraint("training_id", "employee_id", name="uk_hr_trn_att_training_emp"),
        CheckConstraint(
            "attendance_status IN ('registered','attended','absent','completed')",
            name="ck_hr_trn_att_day",
        ),
        CheckConstraint("status IN ('active','cancelled')", name="ck_hr_trn_att_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    training_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_training.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    attendance_status: Mapped[str] = mapped_column(String(30), nullable=False, default="registered")
    completion_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    certificate_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["separation"] = r'''"""HR separation ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrSeparation(Base, *HrTransactionMixin):
    __tablename__ = "hr_separation"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_hr_sep_company_doc"),
        CheckConstraint(
            "separation_type IN ('resignation','termination','retirement')",
            name="ck_hr_sep_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','manager_approved','hr_approved','completed','cancelled')",
            name="ck_hr_sep_status",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    separation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    requested_last_working_date: Mapped[date] = mapped_column(Date, nullable=False)
    approved_last_working_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
    clearance_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
'''

# Class name map for migrations
CLASS_MAP = {
    "designation": "HrDesignation",
    "employee_profile": "HrEmployeeProfile",
    "employment": "HrEmployment",
    "department_assignment": "HrDepartmentAssignment",
    "designation_assignment": "HrDesignationAssignment",
    "shift": "HrShift",
    "shift_assignment": "HrShiftAssignment",
    "holiday_calendar": "HrHolidayCalendar",
    "leave_type": "HrLeaveType",
    "leave_balance": "HrLeaveBalance",
    "leave_request": "HrLeaveRequest",
    "attendance": "HrAttendance",
    "employee_document": "HrEmployeeDocument",
    "performance_review": "HrPerformanceReview",
    "goal": "HrGoal",
    "appraisal": "HrAppraisal",
    "training": "HrTraining",
    "training_attendance": "HrTrainingAttendance",
    "separation": "HrSeparation",
}

REV_ORDER = [
    ("0158_hr_designation", "designation", "0157_create_hr_schema"),
    ("0159_hr_employee_profile", "employee_profile", "0158_hr_designation"),
    ("0160_hr_employment", "employment", "0159_hr_employee_profile"),
    ("0161_hr_department_assignment", "department_assignment", "0160_hr_employment"),
    ("0162_hr_designation_assignment", "designation_assignment", "0161_hr_department_assignment"),
    ("0163_hr_shift", "shift", "0162_hr_designation_assignment"),
    ("0164_hr_shift_assignment", "shift_assignment", "0163_hr_shift"),
    ("0165_hr_holiday_calendar", "holiday_calendar", "0164_hr_shift_assignment"),
    ("0166_hr_leave_type", "leave_type", "0165_hr_holiday_calendar"),
    ("0167_hr_leave_balance", "leave_balance", "0166_hr_leave_type"),
    ("0168_hr_leave_request", "leave_request", "0167_hr_leave_balance"),
    ("0169_hr_attendance", "attendance", "0168_hr_leave_request"),
    ("0170_hr_employee_document", "employee_document", "0169_hr_attendance"),
    ("0171_hr_performance_review", "performance_review", "0170_hr_employee_document"),
    ("0172_hr_goal", "goal", "0171_hr_performance_review"),
    ("0173_hr_appraisal", "appraisal", "0172_hr_goal"),
    ("0174_hr_training", "training", "0173_hr_appraisal"),
    ("0175_hr_training_attendance", "training_attendance", "0174_hr_training"),
    ("0176_hr_separation", "separation", "0175_hr_training_attendance"),
]


def main() -> None:
    for name, content in MODELS.items():
        w(HR / "models" / f"{name}.py", content)

    init_imports = "\n".join(
        f"from modules.hr.models.{k} import {CLASS_MAP[k]}" for k in CLASS_MAP
    )
    all_list = ",\n    ".join(f'"{CLASS_MAP[k]}"' for k in CLASS_MAP)
    w(
        HR / "models" / "__init__.py",
        f'''"""HR ORM models."""

{init_imports}

__all__ = [
    {all_list},
]
''',
    )

    w(
        ALEMBIC / "0157_create_hr_schema.py",
        '''"""Create hr schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0157_create_hr_schema"
down_revision: str | None = "0156_seed_crm_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS hr")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS hr CASCADE")
''',
    )

    for rev, model_key, down in REV_ORDER:
        cls = CLASS_MAP[model_key]
        w(
            ALEMBIC / f"{rev}.py",
            f'''"""Create {cls} table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.hr.models.{model_key} import {cls}  # noqa: F401

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {cls}.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    {cls}.__table__.drop(bind=op.get_bind(), checkfirst=True)
''',
        )

    print("models + migrations 0157-0176 done")


if __name__ == "__main__":
    main()
