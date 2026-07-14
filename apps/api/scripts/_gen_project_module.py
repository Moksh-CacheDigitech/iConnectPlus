"""Generate Sprint 14 Project Management module. Run from apps/api:
python scripts/_gen_project_module.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PRJ = SRC / "modules" / "project"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = SRC / "tests"
SHARED = SRC / "shared"

FILES_WRITTEN: list[Path] = []

OPT_BRANCH = '''
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
'''

WF_FIELDS = '''
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
'''


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")
    FILES_WRITTEN.append(path)
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


# table_key, ORM class, Service/Repo stem, branch_scoped (mandatory BranchMixin)
TABLES: list[tuple[str, str, str, bool]] = [
    ("project", "PrjProject", "Project", True),
    ("project_phase", "PrjProjectPhase", "ProjectPhase", False),
    ("project_milestone", "PrjProjectMilestone", "ProjectMilestone", False),
    ("project_task", "PrjProjectTask", "ProjectTask", True),
    ("task_dependency", "PrjTaskDependency", "TaskDependency", False),
    ("task_assignment", "PrjTaskAssignment", "TaskAssignment", False),
    ("timesheet", "PrjTimesheet", "Timesheet", True),
    ("timesheet_entry", "PrjTimesheetEntry", "TimesheetEntry", True),
    ("resource_plan", "PrjResourcePlan", "ResourcePlan", False),
    ("resource_allocation", "PrjResourceAllocation", "ResourceAllocation", False),
    ("project_budget", "PrjProjectBudget", "ProjectBudget", False),
    ("project_cost", "PrjProjectCost", "ProjectCost", True),
    ("project_issue", "PrjProjectIssue", "ProjectIssue", False),
    ("project_risk", "PrjProjectRisk", "ProjectRisk", False),
    ("change_request", "PrjChangeRequest", "ChangeRequest", True),
    ("project_document", "PrjProjectDocument", "ProjectDocument", False),
    ("project_comment", "PrjProjectComment", "ProjectComment", False),
    ("project_status_history", "PrjProjectStatusHistory", "ProjectStatusHistory", False),
    ("project_notification", "PrjProjectNotification", "ProjectNotification", False),
    ("project_report", "PrjProjectReport", "ProjectReport", False),
]

CLASS_MAP = {t[0]: t[1] for t in TABLES}

MIGRATIONS: list[tuple[str, str | list[str], str]] = [
    ("0223_create_project_schema", "schema", "0222_seed_recruitment_workflows"),
    ("0224_prj_project", "project", "0223_create_project_schema"),
    ("0225_prj_project_phase", "project_phase", "0224_prj_project"),
    ("0226_prj_project_milestone", "project_milestone", "0225_prj_project_phase"),
    ("0227_prj_project_task", "project_task", "0226_prj_project_milestone"),
    ("0228_prj_task_dep_assign", ["task_dependency", "task_assignment"], "0227_prj_project_task"),
    ("0229_prj_timesheet", "timesheet", "0228_prj_task_dep_assign"),
    ("0230_prj_timesheet_entry", "timesheet_entry", "0229_prj_timesheet"),
    ("0231_prj_resource_plan", "resource_plan", "0230_prj_timesheet_entry"),
    ("0232_prj_resource_allocation", "resource_allocation", "0231_prj_resource_plan"),
    ("0233_prj_project_budget", "project_budget", "0232_prj_resource_allocation"),
    ("0234_prj_project_cost", "project_cost", "0233_prj_project_budget"),
    ("0235_prj_project_issue", "project_issue", "0234_prj_project_cost"),
    ("0236_prj_project_risk", "project_risk", "0235_prj_project_issue"),
    ("0237_prj_change_request", "change_request", "0236_prj_project_risk"),
    ("0238_prj_project_document", "project_document", "0237_prj_change_request"),
    ("0239_prj_project_comment", "project_comment", "0238_prj_project_document"),
    ("0240_prj_project_status_hist", "project_status_history", "0239_prj_project_comment"),
    ("0241_prj_project_notification", "project_notification", "0240_prj_project_status_hist"),
    ("0242_prj_project_report", "project_report", "0241_prj_project_notification"),
    ("0243_seed_project_permissions", "seed_perms", "0242_prj_project_report"),
    ("0244_seed_project_workflows", "seed_wf", "0243_seed_project_permissions"),
]

# route prefix, schema/API name, service class, permission resource, branch required
ROUTE_SPECS: list[tuple[str, str, str, str, bool]] = [
    ("projects", "Project", "ProjectService", "project.project", True),
    ("project-phases", "ProjectPhase", "PhaseService", "project.phase", False),
    ("project-milestones", "ProjectMilestone", "MilestoneService", "project.milestone", False),
    ("project-tasks", "ProjectTask", "TaskService", "project.task", True),
    ("task-dependencies", "TaskDependency", "TaskDependencyService", "project.task", False),
    ("task-assignments", "TaskAssignment", "TaskAssignmentService", "project.task", False),
    ("timesheets", "Timesheet", "TimesheetService", "project.timesheet", True),
    ("timesheet-entries", "TimesheetEntry", "TimesheetEntryService", "project.timesheet", True),
    ("resource-plans", "ResourcePlan", "ResourcePlanningService", "project.resource", False),
    ("resource-allocations", "ResourceAllocation", "ResourceAllocationService", "project.resource", False),
    ("project-budgets", "ProjectBudget", "BudgetService", "project.budget", False),
    ("project-costs", "ProjectCost", "CostService", "project.cost", True),
    ("project-issues", "ProjectIssue", "IssueService", "project.issue", False),
    ("project-risks", "ProjectRisk", "RiskService", "project.risk", False),
    ("change-requests", "ChangeRequest", "ChangeRequestService", "project.change_request", True),
    ("project-documents", "ProjectDocument", "DocumentService", "project.document", False),
    ("project-comments", "ProjectComment", "CommentService", "project.comment", False),
    ("project-status-history", "ProjectStatusHistory", "StatusHistoryService", "project.project", False),
    ("project-notifications", "ProjectNotification", "NotificationService", "project.project", False),
    ("reports", "ProjectReport", "ProjectReportService", "project.report", False),
]

# ---------------------------------------------------------------------------
# MODEL BODIES
# ---------------------------------------------------------------------------

MODELS: dict[str, str] = {}

MODELS["project"] = f'''"""Project master ORM per ERD_14 Â§6.1."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjTransactionMixin


class PrjProject(Base, *PrjTransactionMixin):
    __tablename__ = "prj_project"
    __table_args__ = (
        UniqueConstraint("company_id", "project_code", name="uk_prj_project_company_code"),
        CheckConstraint(
            "project_type IN ('internal','customer','rnd','implementation','support')",
            name="ck_prj_project_type",
        ),
        CheckConstraint(
            "billing_type IS NULL OR billing_type IN "
            "('fixed_price','time_material','milestone','retainer')",
            name="ck_prj_project_billing_type",
        ),
        CheckConstraint(
            "health_status IS NULL OR health_status IN ('green','amber','red')",
            name="ck_prj_project_health",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','in_progress','on_hold',"
            "'completed','cancelled','closed')",
            name="ck_prj_project_status",
        ),
        CheckConstraint("planned_end_date >= planned_start_date", name="ck_prj_project_dates"),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_code: Mapped[str] = mapped_column(String(50), nullable=False)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_type: Mapped[str] = mapped_column(String(40), nullable=False)
    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    project_manager_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sponsor_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    budget_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    billing_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    crm_opportunity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    crm_customer_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    health_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["project_phase"] = f'''"""Project phase ORM per ERD_14 Â§6.2."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectPhase(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_phase"
    __table_args__ = (
        UniqueConstraint("project_id", "phase_code", name="uk_prj_phase_project_code"),
        CheckConstraint(
            "status IN ('planned','active','completed','cancelled')",
            name="ck_prj_phase_status",
        ),
        CheckConstraint("planned_end_date >= planned_start_date", name="ck_prj_phase_dates"),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    phase_code: Mapped[str] = mapped_column(String(50), nullable=False)
    phase_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_no: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
'''

MODELS["project_milestone"] = f'''"""Project milestone ORM per ERD_14 Â§6.3."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectMilestone(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_milestone"
    __table_args__ = (
        UniqueConstraint("project_id", "milestone_code", name="uk_prj_ms_project_code"),
        CheckConstraint(
            "status IN ('planned','achieved','delayed','cancelled')",
            name="ck_prj_ms_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    phase_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_phase.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    milestone_code: Mapped[str] = mapped_column(String(50), nullable=False)
    milestone_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    achieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
'''

MODELS["project_task"] = f'''"""Project task ORM per ERD_14 Â§6.4."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjTransactionMixin


class PrjProjectTask(Base, *PrjTransactionMixin):
    __tablename__ = "prj_project_task"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_task_company_doc"),
        CheckConstraint(
            "priority IN ('low','medium','high','critical')",
            name="ck_prj_task_priority",
        ),
        CheckConstraint(
            "status IN ('open','in_progress','blocked','completed','cancelled',"
            "'submitted','approved')",
            name="ck_prj_task_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    phase_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_phase.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    milestone_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_milestone.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    parent_task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    planned_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    estimated_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    actual_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    percent_complete: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
{WF_FIELDS}
'''

MODELS["task_dependency"] = '''"""Task dependency ORM per ERD_14 Â§6.5."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjTaskDependency(Base, *PrjDetailMixin):
    __tablename__ = "prj_task_dependency"
    __table_args__ = (
        UniqueConstraint(
            "from_task_id", "to_task_id", "dependency_type",
            name="uk_prj_task_dep_pair_type",
        ),
        CheckConstraint("from_task_id <> to_task_id", name="ck_prj_task_dep_no_self"),
        CheckConstraint(
            "dependency_type IN ('finish_to_start','start_to_start',"
            "'finish_to_finish','start_to_finish')",
            name="ck_prj_task_dep_type",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_prj_task_dep_status"),
        {"schema": "project"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    from_task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    to_task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    dependency_type: Mapped[str] = mapped_column(String(30), nullable=False, default="finish_to_start")
    lag_days: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["task_assignment"] = f'''"""Task assignment ORM per ERD_14 Â§6.6."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjTaskAssignment(Base, *PrjDetailMixin):
    __tablename__ = "prj_task_assignment"
    __table_args__ = (
        UniqueConstraint("task_id", "employee_id", name="uk_prj_task_assign_emp"),
        CheckConstraint(
            "role_on_task IN ('owner','contributor','reviewer')",
            name="ck_prj_task_assign_role",
        ),
        CheckConstraint(
            "allocation_percent IS NULL OR (allocation_percent >= 0 AND allocation_percent <= 100)",
            name="ck_prj_task_assign_pct",
        ),
        CheckConstraint(
            "status IN ('active','completed','removed')",
            name="ck_prj_task_assign_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role_on_task: Mapped[str] = mapped_column(String(30), nullable=False, default="contributor")
    allocation_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["timesheet"] = f'''"""Timesheet header ORM per ERD_14 Â§6.7."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjTransactionMixin


class PrjTimesheet(Base, *PrjTransactionMixin):
    __tablename__ = "prj_timesheet"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_ts_company_doc"),
        CheckConstraint(
            "status IN ('draft','submitted','approved','rejected','cancelled')",
            name="ck_prj_ts_status",
        ),
        CheckConstraint("period_end >= period_start", name="ck_prj_ts_period"),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    total_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["timesheet_entry"] = f'''"""Timesheet entry ORM per ERD_14 Â§6.8."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjTransactionMixin


class PrjTimesheetEntry(Base, *PrjTransactionMixin):
    __tablename__ = "prj_timesheet_entry"
    __table_args__ = (
        CheckConstraint("hours_worked > 0", name="ck_prj_tse_hours_pos"),
        CheckConstraint("hours_worked <= 24", name="ck_prj_tse_hours_max"),
        CheckConstraint(
            "status IN ('draft','locked','cancelled')",
            name="ck_prj_tse_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    timesheet_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_timesheet.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    work_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hours_worked: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["resource_plan"] = f'''"""Resource plan ORM per ERD_14 Â§6.9."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjResourcePlan(Base, *PrjDetailMixin):
    __tablename__ = "prj_resource_plan"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_rplan_company_doc"),
        CheckConstraint(
            "status IN ('draft','active','closed','cancelled')",
            name="ck_prj_rplan_status",
        ),
        CheckConstraint("planned_to >= planned_from", name="ck_prj_rplan_dates"),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    plan_name: Mapped[str] = mapped_column(String(255), nullable=False)
    planned_from: Mapped[date] = mapped_column(Date, nullable=False)
    planned_to: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["resource_allocation"] = f'''"""Resource allocation ORM per ERD_14 Â§6.10."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjResourceAllocation(Base, *PrjDetailMixin):
    __tablename__ = "prj_resource_allocation"
    __table_args__ = (
        CheckConstraint(
            "resource_type IN ('employee','contractor','consultant','vendor')",
            name="ck_prj_ralloc_type",
        ),
        CheckConstraint(
            "allocation_percent >= 0 AND allocation_percent <= 100",
            name="ck_prj_ralloc_pct",
        ),
        CheckConstraint(
            "status IN ('planned','active','completed','cancelled')",
            name="ck_prj_ralloc_status",
        ),
        CheckConstraint("end_date >= start_date", name="ck_prj_ralloc_dates"),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    resource_plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_resource_plan.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False, default="employee")
    allocation_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
'''

# --- rest of _gen_project_module.py (appended) ---

MODELS["project_budget"] = f'''"""Project budget ORM per ERD_14 Â§6.11."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectBudget(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_budget"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_bud_company_doc"),
        CheckConstraint(
            "budget_type IN ('labor','materials','travel','software','hardware','other')",
            name="ck_prj_bud_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','closed','rejected','cancelled')",
            name="ck_prj_bud_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    budget_type: Mapped[str] = mapped_column(String(30), nullable=False)
    budget_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    fiscal_year_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    cost_center_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    finance_budget_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["project_cost"] = f'''"""Project cost ORM per ERD_14 Â§6.12."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjTransactionMixin


class PrjProjectCost(Base, *PrjTransactionMixin):
    __tablename__ = "prj_project_cost"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_cost_company_doc"),
        UniqueConstraint("tenant_id", "company_id", "idempotency_key", name="uk_prj_cost_idem"),
        CheckConstraint(
            "cost_source IN ('payroll','procurement','expense','asset','vendor_bill','manual')",
            name="ck_prj_cost_source",
        ),
        CheckConstraint(
            "status IN ('draft','posted','failed','reversed','cancelled')",
            name="ck_prj_cost_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cost_source: Mapped[str] = mapped_column(String(30), nullable=False)
    cost_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    cost_date: Mapped[date] = mapped_column(Date, nullable=False)
    employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    timesheet_entry_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_timesheet_entry.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    purchase_request_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    purchase_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    material_issue_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    material_receipt_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    production_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    quality_inspection_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["project_issue"] = f'''"""Project issue ORM per ERD_14 Â§6.13."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectIssue(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_issue"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_iss_company_doc"),
        CheckConstraint(
            "severity IN ('low','medium','high','critical')",
            name="ck_prj_iss_severity",
        ),
        CheckConstraint(
            "status IN ('open','in_progress','resolved','closed','cancelled')",
            name="ck_prj_iss_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    issue_title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
'''

MODELS["project_risk"] = f'''"""Project risk ORM per ERD_14 Â§6.14."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectRisk(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_risk"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_risk_company_doc"),
        CheckConstraint(
            "impact IN ('low','medium','high','critical')",
            name="ck_prj_risk_impact",
        ),
        CheckConstraint(
            "probability IN ('low','medium','high','critical')",
            name="ck_prj_risk_prob",
        ),
        CheckConstraint(
            "risk_level IN ('low','medium','high','critical')",
            name="ck_prj_risk_level",
        ),
        CheckConstraint(
            "status IN ('identified','mitigating','accepted','closed','cancelled')",
            name="ck_prj_risk_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    risk_name: Mapped[str] = mapped_column(String(255), nullable=False)
    impact: Mapped[str] = mapped_column(String(20), nullable=False)
    probability: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    mitigation_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="identified", index=True)
'''

MODELS["change_request"] = f'''"""Change request ORM per ERD_14 Â§6.15."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjTransactionMixin


class PrjChangeRequest(Base, *PrjTransactionMixin):
    __tablename__ = "prj_change_request"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_prj_cr_company_doc"),
        CheckConstraint(
            "change_type IN ('scope','schedule','budget','resource','other')",
            name="ck_prj_cr_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','rejected','implemented','cancelled')",
            name="ck_prj_cr_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    change_title: Mapped[str] = mapped_column(String(255), nullable=False)
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)
    requested_by_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    impact_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_impact_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    schedule_impact_days: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["project_document"] = f'''"""Project document ORM per ERD_14 Â§6.16."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectDocument(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_document"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('brd','design','report','contract','other')",
            name="ck_prj_doc_type",
        ),
        CheckConstraint(
            "status IN ('active','superseded','archived')",
            name="ck_prj_doc_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    milestone_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_milestone.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    uploaded_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["project_comment"] = f'''"""Project comment ORM per ERD_14 Â§6.17."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectComment(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_comment"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','edited','deleted_soft')",
            name="ck_prj_cmt_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project_task.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    issue_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    risk_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    author_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.sec_user.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["project_status_history"] = f'''"""Project status history ORM per ERD_14 Â§6.18."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectStatusHistory(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_status_history"
    __table_args__ = (
        CheckConstraint("status IN ('recorded')", name="ck_prj_hist_status"),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[str] = mapped_column(String(30), nullable=False)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    changed_by_user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.sec_user.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded")
'''

MODELS["project_notification"] = f'''"""Project notification ORM per ERD_14 Â§6.19."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectNotification(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_notification"
    __table_args__ = (
        CheckConstraint(
            "notification_type IN ('task_due','milestone','budget_exceeded',"
            "'risk_review','timesheet','other')",
            name="ck_prj_notif_type",
        ),
        CheckConstraint(
            "delivery_status IN ('pending','sent','failed','read')",
            name="ck_prj_notif_delivery",
        ),
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_prj_notif_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(40), nullable=False)
    recipient_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    recipient_employee_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["project_report"] = f'''"""Project report ORM per ERD_14 Â§6.20."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.project.models.mixins import PrjDetailMixin


class PrjProjectReport(Base, *PrjDetailMixin):
    __tablename__ = "prj_project_report"
    __table_args__ = (
        UniqueConstraint("company_id", "report_code", name="uk_prj_report_company_code"),
        CheckConstraint(
            "report_type IN ('health','budget_variance','profitability',"
            "'resource_utilization','time_summary')",
            name="ck_prj_report_type",
        ),
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_prj_report_status",
        ),
        {{"schema": "project"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    report_code: Mapped[str] = mapped_column(String(80), nullable=False)
    project_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("project.prj_project.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''


ENGINE_FILE_MAP = {
    "Project": "project",
    "ProjectPhase": "project_phase",
    "ProjectMilestone": "project_milestone",
    "ProjectTask": "project_task",
    "TaskDependency": "task_dependency",
    "TaskAssignment": "task_assignment",
    "Timesheet": "timesheet",
    "TimesheetEntry": "timesheet_entry",
    "ResourcePlan": "resource_plan",
    "ResourceAllocation": "resource_allocation",
    "ProjectBudget": "project_budget",
    "ProjectCost": "project_cost",
    "ProjectIssue": "project_issue",
    "ProjectRisk": "project_risk",
    "ChangeRequest": "change_request",
    "ProjectDocument": "project_document",
    "ProjectComment": "project_comment",
    "ProjectStatusHistory": "project_status_history",
    "ProjectNotification": "project_notification",
    "ProjectReport": "project_report",
}

ENGINE_IMPORTS = """
from modules.project.domain.enums import (
    ChangeRequestStatus,
    ProjectBudgetStatus,
    ProjectCommentStatus,
    ProjectCostStatus,
    ProjectDocumentStatus,
    ProjectIssueStatus,
    ProjectMilestoneStatus,
    ProjectNotificationStatus,
    ProjectPhaseStatus,
    ProjectReportStatus,
    ProjectRiskStatus,
    ProjectStatus,
    ProjectTaskStatus,
    ResourceAllocationStatus,
    ResourcePlanStatus,
    TaskAssignmentStatus,
    TaskDependencyStatus,
    TimesheetEntryStatus,
    TimesheetStatus,
)
from modules.project.domain.exceptions import (
    InvalidChangeRequestState,
    InvalidProjectBudgetState,
    InvalidProjectCostState,
    InvalidProjectIssueState,
    InvalidProjectMilestoneState,
    InvalidProjectPhaseState,
    InvalidProjectReportState,
    InvalidProjectRiskState,
    InvalidProjectState,
    InvalidProjectTaskState,
    InvalidResourceAllocationState,
    InvalidResourcePlanState,
    InvalidTaskAssignmentState,
    InvalidTaskDependencyState,
    InvalidTimesheetEntryState,
    InvalidTimesheetState,
)
"""

ENGINE_BODIES: dict[str, str] = {
    "Project": '''
class ProjectEngine:
    def submit(self, row) -> None:
        if row.status != ProjectStatus.DRAFT.value:
            raise InvalidProjectState("Only draft projects can be submitted")
        row.status = ProjectStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ProjectStatus.SUBMITTED.value:
            raise InvalidProjectState("Only submitted projects can be approved")
        row.status = ProjectStatus.APPROVED.value

    def start(self, row) -> None:
        if row.status not in {ProjectStatus.APPROVED.value, ProjectStatus.ON_HOLD.value}:
            raise InvalidProjectState("Project not startable")
        row.status = ProjectStatus.IN_PROGRESS.value

    def hold(self, row) -> None:
        if row.status != ProjectStatus.IN_PROGRESS.value:
            raise InvalidProjectState("Only in-progress projects can be held")
        row.status = ProjectStatus.ON_HOLD.value

    def complete(self, row) -> None:
        if row.status != ProjectStatus.IN_PROGRESS.value:
            raise InvalidProjectState("Only in-progress projects can be completed")
        row.status = ProjectStatus.COMPLETED.value

    def close(self, row) -> None:
        if row.status != ProjectStatus.COMPLETED.value:
            raise InvalidProjectState("Only completed projects can be closed")
        row.status = ProjectStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectStatus.CLOSED.value, ProjectStatus.CANCELLED.value}:
            raise InvalidProjectState("Project already terminal")
        row.status = ProjectStatus.CANCELLED.value
''',
    "ProjectPhase": '''
class ProjectPhaseEngine:
    def activate(self, row) -> None:
        if row.status != ProjectPhaseStatus.PLANNED.value:
            raise InvalidProjectPhaseState("Only planned phases can activate")
        row.status = ProjectPhaseStatus.ACTIVE.value

    def complete(self, row) -> None:
        if row.status != ProjectPhaseStatus.ACTIVE.value:
            raise InvalidProjectPhaseState("Only active phases can complete")
        row.status = ProjectPhaseStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectPhaseStatus.COMPLETED.value, ProjectPhaseStatus.CANCELLED.value}:
            raise InvalidProjectPhaseState("Phase already terminal")
        row.status = ProjectPhaseStatus.CANCELLED.value
''',
    "ProjectMilestone": '''
class ProjectMilestoneEngine:
    def achieve(self, row) -> None:
        if row.status not in {ProjectMilestoneStatus.PLANNED.value, ProjectMilestoneStatus.DELAYED.value}:
            raise InvalidProjectMilestoneState("Milestone not achievable")
        row.status = ProjectMilestoneStatus.ACHIEVED.value

    def delay(self, row) -> None:
        if row.status != ProjectMilestoneStatus.PLANNED.value:
            raise InvalidProjectMilestoneState("Only planned milestones can be delayed")
        row.status = ProjectMilestoneStatus.DELAYED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectMilestoneStatus.ACHIEVED.value, ProjectMilestoneStatus.CANCELLED.value}:
            raise InvalidProjectMilestoneState("Milestone already terminal")
        row.status = ProjectMilestoneStatus.CANCELLED.value
''',
    "ProjectTask": '''
class ProjectTaskEngine:
    def start(self, row) -> None:
        if row.status not in {ProjectTaskStatus.OPEN.value, ProjectTaskStatus.APPROVED.value}:
            raise InvalidProjectTaskState("Task not startable")
        row.status = ProjectTaskStatus.IN_PROGRESS.value

    def block(self, row) -> None:
        if row.status != ProjectTaskStatus.IN_PROGRESS.value:
            raise InvalidProjectTaskState("Only in-progress tasks can be blocked")
        row.status = ProjectTaskStatus.BLOCKED.value

    def complete(self, row) -> None:
        if row.status not in {ProjectTaskStatus.IN_PROGRESS.value, ProjectTaskStatus.BLOCKED.value}:
            raise InvalidProjectTaskState("Task not completable")
        row.status = ProjectTaskStatus.COMPLETED.value

    def submit(self, row) -> None:
        if row.status not in {ProjectTaskStatus.OPEN.value, ProjectTaskStatus.IN_PROGRESS.value}:
            raise InvalidProjectTaskState("Task not submittable")
        row.status = ProjectTaskStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ProjectTaskStatus.SUBMITTED.value:
            raise InvalidProjectTaskState("Only submitted tasks can be approved")
        row.status = ProjectTaskStatus.APPROVED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectTaskStatus.COMPLETED.value, ProjectTaskStatus.CANCELLED.value}:
            raise InvalidProjectTaskState("Task already terminal")
        row.status = ProjectTaskStatus.CANCELLED.value
''',
    "TaskDependency": '''
class TaskDependencyEngine:
    def activate(self, row) -> None:
        row.status = TaskDependencyStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = TaskDependencyStatus.INACTIVE.value
''',
    "TaskAssignment": '''
class TaskAssignmentEngine:
    def complete(self, row) -> None:
        if row.status != TaskAssignmentStatus.ACTIVE.value:
            raise InvalidTaskAssignmentState("Only active assignments can complete")
        row.status = TaskAssignmentStatus.COMPLETED.value

    def remove(self, row) -> None:
        if row.status == TaskAssignmentStatus.REMOVED.value:
            raise InvalidTaskAssignmentState("Assignment already removed")
        row.status = TaskAssignmentStatus.REMOVED.value
''',
    "Timesheet": '''
class TimesheetEngine:
    def submit(self, row) -> None:
        if row.status != TimesheetStatus.DRAFT.value:
            raise InvalidTimesheetState("Only draft timesheets can be submitted")
        row.status = TimesheetStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != TimesheetStatus.SUBMITTED.value:
            raise InvalidTimesheetState("Only submitted timesheets can be approved")
        row.status = TimesheetStatus.APPROVED.value

    def reject(self, row) -> None:
        if row.status != TimesheetStatus.SUBMITTED.value:
            raise InvalidTimesheetState("Only submitted timesheets can be rejected")
        row.status = TimesheetStatus.REJECTED.value

    def cancel(self, row) -> None:
        if row.status in {TimesheetStatus.APPROVED.value, TimesheetStatus.CANCELLED.value}:
            raise InvalidTimesheetState("Timesheet already terminal")
        row.status = TimesheetStatus.CANCELLED.value
''',
    "TimesheetEntry": '''
class TimesheetEntryEngine:
    def lock(self, row) -> None:
        if row.status != TimesheetEntryStatus.DRAFT.value:
            raise InvalidTimesheetEntryState("Only draft entries can be locked")
        row.status = TimesheetEntryStatus.LOCKED.value

    def cancel(self, row) -> None:
        if row.status == TimesheetEntryStatus.CANCELLED.value:
            raise InvalidTimesheetEntryState("Entry already cancelled")
        row.status = TimesheetEntryStatus.CANCELLED.value
''',
    "ResourcePlan": '''
class ResourcePlanEngine:
    def activate(self, row) -> None:
        if row.status != ResourcePlanStatus.DRAFT.value:
            raise InvalidResourcePlanState("Only draft plans can activate")
        row.status = ResourcePlanStatus.ACTIVE.value

    def close(self, row) -> None:
        if row.status != ResourcePlanStatus.ACTIVE.value:
            raise InvalidResourcePlanState("Only active plans can close")
        row.status = ResourcePlanStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ResourcePlanStatus.CLOSED.value, ResourcePlanStatus.CANCELLED.value}:
            raise InvalidResourcePlanState("Plan already terminal")
        row.status = ResourcePlanStatus.CANCELLED.value
''',
    "ResourceAllocation": '''
class ResourceAllocationEngine:
    def activate(self, row) -> None:
        if row.status != ResourceAllocationStatus.PLANNED.value:
            raise InvalidResourceAllocationState("Only planned allocations can activate")
        row.status = ResourceAllocationStatus.ACTIVE.value

    def complete(self, row) -> None:
        if row.status != ResourceAllocationStatus.ACTIVE.value:
            raise InvalidResourceAllocationState("Only active allocations can complete")
        row.status = ResourceAllocationStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status in {ResourceAllocationStatus.COMPLETED.value, ResourceAllocationStatus.CANCELLED.value}:
            raise InvalidResourceAllocationState("Allocation already terminal")
        row.status = ResourceAllocationStatus.CANCELLED.value
''',
    "ProjectBudget": '''
class ProjectBudgetEngine:
    def submit(self, row) -> None:
        if row.status != ProjectBudgetStatus.DRAFT.value:
            raise InvalidProjectBudgetState("Only draft budgets can be submitted")
        row.status = ProjectBudgetStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ProjectBudgetStatus.SUBMITTED.value:
            raise InvalidProjectBudgetState("Only submitted budgets can be approved")
        row.status = ProjectBudgetStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != ProjectBudgetStatus.APPROVED.value:
            raise InvalidProjectBudgetState("Only approved budgets can activate")
        row.status = ProjectBudgetStatus.ACTIVE.value

    def close(self, row) -> None:
        if row.status != ProjectBudgetStatus.ACTIVE.value:
            raise InvalidProjectBudgetState("Only active budgets can close")
        row.status = ProjectBudgetStatus.CLOSED.value

    def reject(self, row) -> None:
        if row.status != ProjectBudgetStatus.SUBMITTED.value:
            raise InvalidProjectBudgetState("Only submitted budgets can be rejected")
        row.status = ProjectBudgetStatus.REJECTED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectBudgetStatus.CLOSED.value, ProjectBudgetStatus.CANCELLED.value}:
            raise InvalidProjectBudgetState("Budget already terminal")
        row.status = ProjectBudgetStatus.CANCELLED.value
''',
    "ProjectCost": '''
class ProjectCostEngine:
    def post(self, row) -> None:
        if row.status != ProjectCostStatus.DRAFT.value:
            raise InvalidProjectCostState("Only draft costs can be posted")
        row.status = ProjectCostStatus.POSTED.value

    def fail(self, row) -> None:
        if row.status != ProjectCostStatus.DRAFT.value:
            raise InvalidProjectCostState("Only draft costs can fail")
        row.status = ProjectCostStatus.FAILED.value

    def reverse(self, row) -> None:
        if row.status != ProjectCostStatus.POSTED.value:
            raise InvalidProjectCostState("Only posted costs can be reversed")
        row.status = ProjectCostStatus.REVERSED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectCostStatus.POSTED.value, ProjectCostStatus.CANCELLED.value}:
            raise InvalidProjectCostState("Cost already terminal")
        row.status = ProjectCostStatus.CANCELLED.value
''',
    "ProjectIssue": '''
class ProjectIssueEngine:
    def start(self, row) -> None:
        if row.status != ProjectIssueStatus.OPEN.value:
            raise InvalidProjectIssueState("Only open issues can start")
        row.status = ProjectIssueStatus.IN_PROGRESS.value

    def resolve(self, row) -> None:
        if row.status != ProjectIssueStatus.IN_PROGRESS.value:
            raise InvalidProjectIssueState("Only in-progress issues can resolve")
        row.status = ProjectIssueStatus.RESOLVED.value

    def close(self, row) -> None:
        if row.status != ProjectIssueStatus.RESOLVED.value:
            raise InvalidProjectIssueState("Only resolved issues can close")
        row.status = ProjectIssueStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectIssueStatus.CLOSED.value, ProjectIssueStatus.CANCELLED.value}:
            raise InvalidProjectIssueState("Issue already terminal")
        row.status = ProjectIssueStatus.CANCELLED.value
''',
    "ProjectRisk": '''
class ProjectRiskEngine:
    def mitigate(self, row) -> None:
        if row.status != ProjectRiskStatus.IDENTIFIED.value:
            raise InvalidProjectRiskState("Only identified risks can mitigate")
        row.status = ProjectRiskStatus.MITIGATING.value

    def accept(self, row) -> None:
        if row.status not in {ProjectRiskStatus.IDENTIFIED.value, ProjectRiskStatus.MITIGATING.value}:
            raise InvalidProjectRiskState("Risk not acceptable")
        row.status = ProjectRiskStatus.ACCEPTED.value

    def close(self, row) -> None:
        if row.status not in {ProjectRiskStatus.MITIGATING.value, ProjectRiskStatus.ACCEPTED.value}:
            raise InvalidProjectRiskState("Risk not closable")
        row.status = ProjectRiskStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ProjectRiskStatus.CLOSED.value, ProjectRiskStatus.CANCELLED.value}:
            raise InvalidProjectRiskState("Risk already terminal")
        row.status = ProjectRiskStatus.CANCELLED.value
''',
    "ChangeRequest": '''
class ChangeRequestEngine:
    def submit(self, row) -> None:
        if row.status != ChangeRequestStatus.DRAFT.value:
            raise InvalidChangeRequestState("Only draft change requests can be submitted")
        row.status = ChangeRequestStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ChangeRequestStatus.SUBMITTED.value:
            raise InvalidChangeRequestState("Only submitted change requests can be approved")
        row.status = ChangeRequestStatus.APPROVED.value

    def reject(self, row) -> None:
        if row.status != ChangeRequestStatus.SUBMITTED.value:
            raise InvalidChangeRequestState("Only submitted change requests can be rejected")
        row.status = ChangeRequestStatus.REJECTED.value

    def implement(self, row) -> None:
        if row.status != ChangeRequestStatus.APPROVED.value:
            raise InvalidChangeRequestState("Only approved change requests can be implemented")
        row.status = ChangeRequestStatus.IMPLEMENTED.value

    def cancel(self, row) -> None:
        if row.status in {ChangeRequestStatus.IMPLEMENTED.value, ChangeRequestStatus.CANCELLED.value}:
            raise InvalidChangeRequestState("Change request already terminal")
        row.status = ChangeRequestStatus.CANCELLED.value
''',
    "ProjectDocument": '''
class ProjectDocumentEngine:
    def supersede(self, row) -> None:
        if row.status != ProjectDocumentStatus.ACTIVE.value:
            raise InvalidProjectState("Only active documents can be superseded")
        row.status = ProjectDocumentStatus.SUPERSEDED.value

    def archive(self, row) -> None:
        if row.status not in {ProjectDocumentStatus.ACTIVE.value, ProjectDocumentStatus.SUPERSEDED.value}:
            raise InvalidProjectState("Document not archivable")
        row.status = ProjectDocumentStatus.ARCHIVED.value
''',
    "ProjectComment": '''
class ProjectCommentEngine:
    def edit(self, row) -> None:
        if row.status not in {ProjectCommentStatus.ACTIVE.value, ProjectCommentStatus.EDITED.value}:
            raise InvalidProjectState("Comment not editable")
        row.status = ProjectCommentStatus.EDITED.value

    def soft_delete(self, row) -> None:
        row.status = ProjectCommentStatus.DELETED_SOFT.value
''',
    "ProjectStatusHistory": '''
class ProjectStatusHistoryEngine:
    def record(self, row) -> None:
        row.status = "recorded"
''',
    "ProjectNotification": '''
class ProjectNotificationEngine:
    def archive(self, row) -> None:
        if row.status != ProjectNotificationStatus.ACTIVE.value:
            raise InvalidProjectState("Only active notifications can archive")
        row.status = ProjectNotificationStatus.ARCHIVED.value
''',
    "ProjectReport": '''
class ProjectReportEngine:
    def finalize(self, row) -> None:
        if row.status != ProjectReportStatus.DRAFT.value:
            raise InvalidProjectReportState("Only draft reports can finalize")
        row.status = ProjectReportStatus.FINALIZED.value
''',
}


def gen_scaffold() -> None:
    w(PRJ / "__init__.py", '"""Project Management module â€” Sprint 14."""\n')
    w(PRJ / "domain" / "__init__.py", '"""Project domain layer."""\n')
    w(PRJ / "adapters" / "__init__.py", '"""Project cross-module adapters."""\n')
    w(PRJ / "service" / "__init__.py", '"""Project services â€” populated after generation."""\n')
    w(PRJ / "service" / "engines" / "__init__.py", '"""Project engines â€” populated after generation."""\n')
    w(PRJ / "repository" / "__init__.py", '"""Project repositories."""\n')
    w(PRJ / "models" / "__init__.py", '"""Project models â€” populated after generation."""\n')
    w(
        PRJ / "models" / "mixins.py",
        '''"""Project ORM mixin bundles per ERD_14."""

from database.mixins import (
    AuditMixin,
    BranchMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

PrjMasterMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)

PrjTransactionMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    BranchMixin,
    SoftDeleteMixin,
    VersionMixin,
)

PrjDetailMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)
''',
    )


def gen_domain() -> None:
    w(
        PRJ / "domain" / "enums.py",
        '''"""Project domain enums per ERD_14 Â§11."""

from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class ProjectPhaseStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectMilestoneStatus(str, Enum):
    PLANNED = "planned"
    ACHIEVED = "achieved"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class ProjectTaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SUBMITTED = "submitted"
    APPROVED = "approved"


class TaskDependencyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class TaskAssignmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    REMOVED = "removed"


class TimesheetStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class TimesheetEntryStatus(str, Enum):
    DRAFT = "draft"
    LOCKED = "locked"
    CANCELLED = "cancelled"


class ResourcePlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ResourceAllocationStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectBudgetStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    CLOSED = "closed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ProjectCostStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    FAILED = "failed"
    REVERSED = "reversed"
    CANCELLED = "cancelled"


class ProjectIssueStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ProjectRiskStatus(str, Enum):
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    ACCEPTED = "accepted"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ChangeRequestStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class ProjectDocumentStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ProjectCommentStatus(str, Enum):
    ACTIVE = "active"
    EDITED = "edited"
    DELETED_SOFT = "deleted_soft"


class ProjectNotificationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ProjectReportStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class PrjEntityType(str, Enum):
    PROJECT = "project"
    PROJECT_TASK = "project_task"
    TIMESHEET = "timesheet"
    RESOURCE_PLAN = "resource_plan"
    PROJECT_BUDGET = "project_budget"
    PROJECT_COST = "project_cost"
    PROJECT_ISSUE = "project_issue"
    PROJECT_RISK = "project_risk"
    CHANGE_REQUEST = "change_request"
    PROJECT_REPORT = "project_report"


CODE_PREFIXES: dict[PrjEntityType, tuple[str, int, bool]] = {
    PrjEntityType.PROJECT: ("PRJ-", 6, True),
    PrjEntityType.PROJECT_TASK: ("TASK-", 6, True),
    PrjEntityType.TIMESHEET: ("TS-", 6, True),
    PrjEntityType.RESOURCE_PLAN: ("RPLAN-", 6, True),
    PrjEntityType.PROJECT_BUDGET: ("PBUD-", 6, True),
    PrjEntityType.PROJECT_COST: ("PCOST-", 6, True),
    PrjEntityType.PROJECT_ISSUE: ("PISS-", 6, True),
    PrjEntityType.PROJECT_RISK: ("PRISK-", 6, True),
    PrjEntityType.CHANGE_REQUEST: ("PCR-", 6, True),
    PrjEntityType.PROJECT_REPORT: ("PRPT-", 6, True),
}
''',
    )

    exc_lines = []
    for _, _, name, _ in TABLES:
        exc_lines.append(
            f'''
class Invalid{name}State(ConflictException):
    def __init__(self, message: str = "Invalid {name.lower()} state") -> None:
        super().__init__(message)
'''
        )
    w(
        PRJ / "domain" / "exceptions.py",
        '"""Project domain exceptions."""\n\nfrom core.exceptions import ConflictException\n'
        + "".join(exc_lines),
    )
    w(
        PRJ / "domain" / "value_objects.py",
        '''"""Project value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProjectBudgetLine:
    budget_type: str
    budget_amount: Decimal
    currency_code: str


@dataclass(frozen=True)
class ProjectHealthSnapshot:
    health_status: str
    overdue_tasks: int
    budget_variance: Decimal | None = None
''',
    )
    agg_lines = "\n".join(f'    {t[2].upper()} = "prj_{t[0]}"' for t in TABLES)
    w(
        PRJ / "domain" / "entities.py",
        f'''"""Project domain entity markers."""

from enum import Enum


class PrjAggregate(str, Enum):
{agg_lines}
''',
    )


def gen_models() -> None:
    for name, content in MODELS.items():
        w(PRJ / "models" / f"{name}.py", content)
    init_imports = "\n".join(
        f"from modules.project.models.{k} import {CLASS_MAP[k]}" for k in CLASS_MAP
    )
    all_list = ",\n    ".join(f'"{CLASS_MAP[k]}"' for k in CLASS_MAP)
    w(
        PRJ / "models" / "__init__.py",
        f'''"""Project ORM models."""

{init_imports}

__all__ = [
    {all_list},
]
''',
    )

# --- rest B: migrations through main ---

def gen_migrations() -> None:
    w(
        ALEMBIC / "0223_create_project_schema.py",
        '''"""Create project schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0223_create_project_schema"
down_revision: str | None = "0222_seed_recruitment_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS project")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS project CASCADE")
''',
    )
    for rev, target, down in MIGRATIONS:
        if target == "schema" or (isinstance(target, str) and target.startswith("seed")):
            continue
        if isinstance(target, list):
            imports = "\n".join(
                f"from modules.project.models.{m} import {CLASS_MAP[m]}  # noqa: F401"
                for m in target
            )
            creates = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.create(bind=op.get_bind(), checkfirst=True)" for m in target
            )
            drops = "\n    ".join(
                f"{CLASS_MAP[m]}.__table__.drop(bind=op.get_bind(), checkfirst=True)"
                for m in reversed(target)
            )
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create project graph tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

{imports}

revision: str = "{rev}"
down_revision: str | None = "{down}"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    {creates}


def downgrade() -> None:
    {drops}
''',
            )
        else:
            cls = CLASS_MAP[target]
            w(
                ALEMBIC / f"{rev}.py",
                f'''"""Create {cls} table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.project.models.{target} import {cls}  # noqa: F401

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


def repo_template(module: str, cls: str, name: str, branch: bool) -> str:
    return f'''"""Project {cls} repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.project.models import {cls}
from modules.project.repository.base import PrjScopedRepository, utcnow


class {name}Repository(PrjScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls} | None:
        stmt = select({cls}).where({cls}.id == row_id, {cls}.is_deleted.is_(False))
        stmt = self.apply_prj_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select({cls}).where(
            {cls}.company_id == company_id,
            {cls}.is_deleted.is_(False),
        )
        stmt = self.apply_prj_filter(stmt, {cls}, ctx, branch_scoped={branch})
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


def gen_repos() -> None:
    w(
        PRJ / "repository" / "base.py",
        '''"""Project scoped repository base."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PrjScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_prj_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = PrjScopedRepository.apply_tenant_filter(stmt, model, ctx)
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
            PrjScopedRepository.ensure_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
''',
    )
    w(
        PRJ / "repository" / "code_sequence_repository.py",
        '''"""Project document code sequences."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.project.domain.enums import CODE_PREFIXES, PrjEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: PrjEntityType, company_id: UUID, model, code_column: str) -> str:
        prefix, width, include_year = CODE_PREFIXES[entity]
        year = datetime.now(timezone.utc).year
        full_prefix = f"{prefix}{year}-" if include_year else prefix
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
        w(PRJ / "repository" / f"{module}_repository.py", repo_template(module, cls, name, branch))


def gen_engines() -> None:
    for eng_name, body in ENGINE_BODIES.items():
        fname = ENGINE_FILE_MAP[eng_name]
        w(
            PRJ / "service" / "engines" / f"{fname}_engine.py",
            f'"""{eng_name} lifecycle engine."""\n{ENGINE_IMPORTS}\n{body}\n',
        )
    lines = [
        f"from modules.project.service.engines.{ENGINE_FILE_MAP[n]}_engine import {n}Engine"
        for n in ENGINE_BODIES
    ]
    all_names = ",\n    ".join(f'"{n}Engine"' for n in ENGINE_BODIES)
    w(
        PRJ / "service" / "engines" / "__init__.py",
        '"""Project business engines."""\n\n'
        + "\n".join(lines)
        + f"\n\n__all__ = [\n    {all_names},\n]\n",
    )


def catalog_service(
    svc_name: str,
    cls: str,
    repo_name: str,
    entity: str,
    branch: bool,
    engine_name: str | None = None,
) -> str:
    eng = engine_name or repo_name
    branch_arg = ", *, branch_id: UUID | None = None" if branch else ""
    branch_fields = (
        "\n        if branch_id is not None:\n"
        "            self._scope.validate_branch_access(ctx, branch_id)\n"
        if branch
        else ""
    )
    branch_create = "branch_id=branch_id," if branch else ""
    return f'''"""{svc_name} application service."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.project.models import {cls}
from modules.project.repository.{entity}_repository import {repo_name}Repository
from modules.project.service.engines import {eng}Engine
from modules.project.service.project_scope_validator import ProjectScopeValidator


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = ProjectScopeValidator(db)
        self._engine = {eng}Engine()
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row

    def create(self, ctx: TenantContext, company_id: UUID | None = None{branch_arg}, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
{branch_fields}
        row = self._repo.create(ctx, company_id=cid, {branch_create} **fields)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="prj_{entity}",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return row

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row
'''


def numbered_service(
    svc_name: str,
    cls: str,
    repo_name: str,
    entity: str,
    entity_type: str,
    code_col: str,
    branch_required: bool,
    engine_name: str,
    actions: list[str],
) -> str:
    branch_sig = ", *, branch_id: UUID" if branch_required else ", company_id: UUID | None = None"
    if branch_required:
        create_body = f'''
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PrjEntityType.{entity_type}, cid, {cls}, "{code_col}")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, {code_col}=doc, **fields)
'''
        create_sig = "self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields"
    else:
        create_body = f'''
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(PrjEntityType.{entity_type}, cid, {cls}, "{code_col}")
        return self._repo.create(ctx, company_id=cid, {code_col}=doc, **fields)
'''
        create_sig = "self, ctx: TenantContext, company_id: UUID | None = None, **fields"

    action_methods = ""
    for act in actions:
        action_methods += f'''
    def {act}(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.{act}(row)
        return self._repo.update(ctx, row_id, status=row.status)
'''

    return f'''"""{svc_name}."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.project.domain.enums import PrjEntityType
from modules.project.models import {cls}
from modules.project.repository.{entity}_repository import {repo_name}Repository
from modules.project.service.document_number_service import DocumentNumberService
from modules.project.service.engines import {engine_name}Engine
from modules.project.service.project_scope_validator import ProjectScopeValidator


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = ProjectScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = {engine_name}Engine()
        self._audit = AuditService(db)
        self._db = db

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls}:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row

    def create({create_sig}):
{create_body}
    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("{svc_name} not found")
        return row
{action_methods}
'''


def gen_services() -> None:
    w(
        PRJ / "service" / "project_scope_validator.py",
        '''"""Project scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.project.repository.base import PrjScopedRepository


class ProjectScopeValidator(PrjScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id)
''',
    )
    w(
        PRJ / "service" / "document_number_service.py",
        '''"""Project document numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.project.domain.enums import PrjEntityType
from modules.project.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: PrjEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
''',
    )

    # Catalog / simple services
    simple = [
        ("PhaseService", "PrjProjectPhase", "ProjectPhase", "project_phase", False, "ProjectPhase"),
        ("MilestoneService", "PrjProjectMilestone", "ProjectMilestone", "project_milestone", False, "ProjectMilestone"),
        ("TaskDependencyService", "PrjTaskDependency", "TaskDependency", "task_dependency", False, "TaskDependency"),
        ("TaskAssignmentService", "PrjTaskAssignment", "TaskAssignment", "task_assignment", False, "TaskAssignment"),
        ("TimesheetEntryService", "PrjTimesheetEntry", "TimesheetEntry", "timesheet_entry", True, "TimesheetEntry"),
        ("ResourceAllocationService", "PrjResourceAllocation", "ResourceAllocation", "resource_allocation", False, "ResourceAllocation"),
        ("DocumentService", "PrjProjectDocument", "ProjectDocument", "project_document", False, "ProjectDocument"),
        ("CommentService", "PrjProjectComment", "ProjectComment", "project_comment", False, "ProjectComment"),
        ("StatusHistoryService", "PrjProjectStatusHistory", "ProjectStatusHistory", "project_status_history", False, "ProjectStatusHistory"),
        ("NotificationService", "PrjProjectNotification", "ProjectNotification", "project_notification", False, "ProjectNotification"),
    ]
    for svc, cls, repo, entity, branch, eng in simple:
        w(
            PRJ / "service" / f"{svc.replace('Service','').lower().replace('phase','phase').rstrip('_')}_service.py"
            if False
            else PRJ / "service" / {
                "PhaseService": "phase_service.py",
                "MilestoneService": "milestone_service.py",
                "TaskDependencyService": "task_dependency_service.py",
                "TaskAssignmentService": "task_assignment_service.py",
                "TimesheetEntryService": "timesheet_entry_service.py",
                "ResourceAllocationService": "resource_allocation_service.py",
                "DocumentService": "document_service.py",
                "CommentService": "comment_service.py",
                "StatusHistoryService": "status_history_service.py",
                "NotificationService": "notification_service.py",
            }[svc],
            catalog_service(svc, cls, repo, entity, branch, eng),
        )

    w(
        PRJ / "service" / "project_service.py",
        numbered_service(
            "ProjectService",
            "PrjProject",
            "Project",
            "project",
            "PROJECT",
            "project_code",
            True,
            "Project",
            ["submit", "approve", "close"],
        ),
    )
    # Fix project create to not require project_code from numbers incorrectly for fields
    # numbered_service already handles it

    w(
        PRJ / "service" / "task_service.py",
        numbered_service(
            "TaskService",
            "PrjProjectTask",
            "ProjectTask",
            "project_task",
            "PROJECT_TASK",
            "document_number",
            True,
            "ProjectTask",
            ["submit", "approve", "complete"],
        ),
    )
    w(
        PRJ / "service" / "timesheet_service.py",
        numbered_service(
            "TimesheetService",
            "PrjTimesheet",
            "Timesheet",
            "timesheet",
            "TIMESHEET",
            "document_number",
            True,
            "Timesheet",
            ["submit", "approve"],
        ),
    )
    w(
        PRJ / "service" / "resource_planning_service.py",
        numbered_service(
            "ResourcePlanningService",
            "PrjResourcePlan",
            "ResourcePlan",
            "resource_plan",
            "RESOURCE_PLAN",
            "document_number",
            False,
            "ResourcePlan",
            ["activate", "close"],
        ),
    )
    w(
        PRJ / "service" / "budget_service.py",
        numbered_service(
            "BudgetService",
            "PrjProjectBudget",
            "ProjectBudget",
            "project_budget",
            "PROJECT_BUDGET",
            "document_number",
            False,
            "ProjectBudget",
            ["submit", "approve"],
        ),
    )
    w(
        PRJ / "service" / "issue_service.py",
        numbered_service(
            "IssueService",
            "PrjProjectIssue",
            "ProjectIssue",
            "project_issue",
            "PROJECT_ISSUE",
            "document_number",
            False,
            "ProjectIssue",
            ["start", "resolve", "close"],
        ),
    )
    w(
        PRJ / "service" / "risk_service.py",
        numbered_service(
            "RiskService",
            "PrjProjectRisk",
            "ProjectRisk",
            "project_risk",
            "PROJECT_RISK",
            "document_number",
            False,
            "ProjectRisk",
            ["mitigate", "accept", "close"],
        ),
    )
    w(
        PRJ / "service" / "change_request_service.py",
        numbered_service(
            "ChangeRequestService",
            "PrjChangeRequest",
            "ChangeRequest",
            "change_request",
            "CHANGE_REQUEST",
            "document_number",
            True,
            "ChangeRequest",
            ["submit", "approve"],
        ),
    )
    w(
        PRJ / "service" / "project_report_service.py",
        numbered_service(
            "ProjectReportService",
            "PrjProjectReport",
            "ProjectReport",
            "project_report",
            "PROJECT_REPORT",
            "report_code",
            False,
            "ProjectReport",
            ["finalize"],
        ),
    )

    w(
        PRJ / "service" / "cost_service.py",
        '''"""Project cost service â€” posts via Finance PostingService only."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.project.adapters.finance_port import ProjectFinanceAdapter
from modules.project.domain.enums import PrjEntityType
from modules.project.models import PrjProjectCost
from modules.project.repository.project_cost_repository import ProjectCostRepository
from modules.project.service.document_number_service import DocumentNumberService
from modules.project.service.engines import ProjectCostEngine
from modules.project.service.project_scope_validator import ProjectScopeValidator


class CostService:
    def __init__(self, db: Session) -> None:
        self._repo = ProjectCostRepository(db)
        self._scope = ProjectScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ProjectCostEngine()
        self._finance = ProjectFinanceAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> PrjProjectCost:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("CostService not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(PrjEntityType.PROJECT_COST, cid, PrjProjectCost, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("CostService not found")
        return row

    def post(
        self,
        ctx: TenantContext,
        row_id: UUID,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ):
        row = self.get(ctx, row_id)
        try:
            journal_id = self._finance.post_project_cost(
                ctx,
                row,
                amount=Decimal(str(row.cost_amount)),
                debit_account_id=debit_account_id,
                credit_account_id=credit_account_id,
                fiscal_year_id=fiscal_year_id,
            )
            self._engine.post(row)
            return self._repo.update(
                ctx, row_id, status=row.status, finance_journal_id=journal_id
            )
        except Exception:
            self._engine.fail(row)
            self._repo.update(ctx, row_id, status=row.status)
            raise
''',
    )
    w(
        PRJ / "service" / "integration_service.py",
        '''"""Project integration service â€” cross-module reads only."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.project.adapters.master_data_port import ProjectMasterDataAdapter
from modules.project.adapters.organization_port import ProjectOrganizationAdapter
from modules.project.adapters.payroll_port import ProjectPayrollAdapter


class ProjectIntegrationService:
    def __init__(self, db: Session) -> None:
        self._master = ProjectMasterDataAdapter(db)
        self._org = ProjectOrganizationAdapter(db)
        self._payroll = ProjectPayrollAdapter(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._master.get_customer(ctx, customer_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._master.get_product(ctx, product_id)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        return self._org.get_department(ctx, department_id)

    def labor_cost_hint(self, ctx: TenantContext, employee_id: UUID):
        return self._payroll.labor_cost_hint(ctx, employee_id)
''',
    )
    w(
        PRJ / "service" / "application_service.py",
        '''"""Project application service facade."""

from sqlalchemy.orm import Session

from modules.project.service.budget_service import BudgetService
from modules.project.service.change_request_service import ChangeRequestService
from modules.project.service.comment_service import CommentService
from modules.project.service.cost_service import CostService
from modules.project.service.document_service import DocumentService
from modules.project.service.integration_service import ProjectIntegrationService
from modules.project.service.issue_service import IssueService
from modules.project.service.milestone_service import MilestoneService
from modules.project.service.notification_service import NotificationService
from modules.project.service.phase_service import PhaseService
from modules.project.service.project_report_service import ProjectReportService
from modules.project.service.project_service import ProjectService
from modules.project.service.resource_allocation_service import ResourceAllocationService
from modules.project.service.resource_planning_service import ResourcePlanningService
from modules.project.service.risk_service import RiskService
from modules.project.service.status_history_service import StatusHistoryService
from modules.project.service.task_assignment_service import TaskAssignmentService
from modules.project.service.task_dependency_service import TaskDependencyService
from modules.project.service.task_service import TaskService
from modules.project.service.timesheet_entry_service import TimesheetEntryService
from modules.project.service.timesheet_service import TimesheetService


class ProjectApplicationService:
    def __init__(self, db: Session) -> None:
        self.projects = ProjectService(db)
        self.phases = PhaseService(db)
        self.milestones = MilestoneService(db)
        self.tasks = TaskService(db)
        self.dependencies = TaskDependencyService(db)
        self.assignments = TaskAssignmentService(db)
        self.timesheets = TimesheetService(db)
        self.timesheet_entries = TimesheetEntryService(db)
        self.resource_plans = ResourcePlanningService(db)
        self.resource_allocations = ResourceAllocationService(db)
        self.budgets = BudgetService(db)
        self.costs = CostService(db)
        self.issues = IssueService(db)
        self.risks = RiskService(db)
        self.change_requests = ChangeRequestService(db)
        self.documents = DocumentService(db)
        self.comments = CommentService(db)
        self.status_history = StatusHistoryService(db)
        self.notifications = NotificationService(db)
        self.reports = ProjectReportService(db)
        self.integration = ProjectIntegrationService(db)
''',
    )

    svc_exports = [
        "BudgetService",
        "ChangeRequestService",
        "CommentService",
        "CostService",
        "DocumentService",
        "IssueService",
        "MilestoneService",
        "NotificationService",
        "PhaseService",
        "ProjectApplicationService",
        "ProjectIntegrationService",
        "ProjectReportService",
        "ProjectService",
        "ResourceAllocationService",
        "ResourcePlanningService",
        "RiskService",
        "StatusHistoryService",
        "TaskAssignmentService",
        "TaskDependencyService",
        "TaskService",
        "TimesheetEntryService",
        "TimesheetService",
    ]
    imports = "\n".join(
        f"from modules.project.service.{n.replace('Service','').lower() if False else ''}"
        for n in []
    )
    # explicit map
    file_map = {
        "BudgetService": "budget_service",
        "ChangeRequestService": "change_request_service",
        "CommentService": "comment_service",
        "CostService": "cost_service",
        "DocumentService": "document_service",
        "IssueService": "issue_service",
        "MilestoneService": "milestone_service",
        "NotificationService": "notification_service",
        "PhaseService": "phase_service",
        "ProjectApplicationService": "application_service",
        "ProjectIntegrationService": "integration_service",
        "ProjectReportService": "project_report_service",
        "ProjectService": "project_service",
        "ResourceAllocationService": "resource_allocation_service",
        "ResourcePlanningService": "resource_planning_service",
        "RiskService": "risk_service",
        "StatusHistoryService": "status_history_service",
        "TaskAssignmentService": "task_assignment_service",
        "TaskDependencyService": "task_dependency_service",
        "TaskService": "task_service",
        "TimesheetEntryService": "timesheet_entry_service",
        "TimesheetService": "timesheet_service",
    }
    import_lines = "\n".join(
        f"from modules.project.service.{file_map[n]} import {n}" for n in svc_exports
    )
    all_list = ",\n    ".join(f'"{n}"' for n in svc_exports)
    w(
        PRJ / "service" / "__init__.py",
        f'''"""Project services."""

{import_lines}

__all__ = [
    {all_list},
]
''',
    )

# --- rest C: adapters, permissions, api, tests, seeds, wiring ---

def gen_adapters() -> None:
    w(
        PRJ / "adapters" / "master_data_port.py",
        '''"""Master Data port â€” read employee / customer / product (C-01)."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.customer_service import CustomerService
from modules.master_data.service.employee_service import EmployeeService
from modules.master_data.service.product_service import ProductService


class ProjectMasterDataAdapter:
    def __init__(self, db: Session) -> None:
        self._employees = EmployeeService(db)
        self._customers = CustomerService(db)
        self._products = ProductService(db)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._employees.get_employee(ctx, employee_id)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._customers.get_customer(ctx, customer_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._products.get_product(ctx, product_id)
''',
    )
    w(
        PRJ / "adapters" / "organization_port.py",
        '''"""Organization port â€” read org_department only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.hierarchy_repository import DepartmentRepository


class ProjectOrganizationAdapter:
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
        PRJ / "adapters" / "finance_port.py",
        '''"""Finance port â€” JournalService + PostingService.post_system_journal only."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.enums import JournalType
from modules.finance.service.journal_service import JournalService
from modules.finance.service.posting_service import PostingService
from modules.foundation.domain.value_objects import TenantContext
from modules.project.models import PrjProjectCost


class ProjectFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._journals = JournalService(db)
        self._posting = PostingService(db)

    def post_project_cost(
        self,
        ctx: TenantContext,
        cost: PrjProjectCost,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        amount = amount.quantize(Decimal("0.0001"))
        journal = self._journals.create_journal(
            ctx,
            company_id=cost.company_id,
            branch_id=cost.branch_id,
            journal_date=cost.cost_date,
            description=f"Project cost {cost.document_number}",
            journal_type=JournalType.SYSTEM.value,
            fiscal_year_id=fiscal_year_id,
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=1,
            account_id=debit_account_id,
            debit_amount=float(amount),
            credit_amount=0,
            description="Project cost expense",
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=2,
            account_id=credit_account_id,
            debit_amount=0,
            credit_amount=float(amount),
            description="Project cost offset",
        )
        self._posting.post_system_journal(ctx, journal.id)
        return journal.id
''',
    )
    w(
        PRJ / "adapters" / "payroll_port.py",
        '''"""Payroll port â€” optional read-only labor cost hint; no pay_* writes."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.repository.employee_salary_repository import EmployeeSalaryRepository


class ProjectPayrollAdapter:
    def __init__(self, db: Session) -> None:
        self._salaries = EmployeeSalaryRepository(db)

    def labor_cost_hint(self, ctx: TenantContext, employee_id: UUID):
        rows = self._salaries.list_rows(ctx, ctx.company_id) if ctx.company_id else []
        for row in rows:
            if getattr(row, "employee_id", None) == employee_id and not getattr(
                row, "is_deleted", False
            ):
                return {
                    "employee_id": employee_id,
                    "salary_id": row.id,
                    "status": getattr(row, "status", None),
                }
        return {"employee_id": employee_id, "hint": None}
''',
    )
    w(
        PRJ / "adapters" / "__init__.py",
        '''"""Project adapters."""

from modules.project.adapters.finance_port import ProjectFinanceAdapter
from modules.project.adapters.master_data_port import ProjectMasterDataAdapter
from modules.project.adapters.organization_port import ProjectOrganizationAdapter
from modules.project.adapters.payroll_port import ProjectPayrollAdapter

__all__ = [
    "ProjectFinanceAdapter",
    "ProjectMasterDataAdapter",
    "ProjectOrganizationAdapter",
    "ProjectPayrollAdapter",
]
''',
    )


def gen_permissions() -> None:
    w(
        PRJ / "permissions.py",
        '''"""Project permission constants per ERD_14 Â§14."""

PROJECT_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("project.project:read", "project.project", "read", "project"),
    ("project.project:create", "project.project", "create", "project"),
    ("project.project:update", "project.project", "update", "project"),
    ("project.project:submit", "project.project", "submit", "project"),
    ("project.project:approve", "project.project", "approve", "project"),
    ("project.project:close", "project.project", "close", "project"),
    ("project.phase:read", "project.phase", "read", "project"),
    ("project.phase:create", "project.phase", "create", "project"),
    ("project.phase:update", "project.phase", "update", "project"),
    ("project.phase:complete", "project.phase", "complete", "project"),
    ("project.milestone:read", "project.milestone", "read", "project"),
    ("project.milestone:create", "project.milestone", "create", "project"),
    ("project.milestone:update", "project.milestone", "update", "project"),
    ("project.milestone:complete", "project.milestone", "complete", "project"),
    ("project.task:read", "project.task", "read", "project"),
    ("project.task:create", "project.task", "create", "project"),
    ("project.task:update", "project.task", "update", "project"),
    ("project.task:complete", "project.task", "complete", "project"),
    ("project.task:approve", "project.task", "approve", "project"),
    ("project.timesheet:read", "project.timesheet", "read", "project"),
    ("project.timesheet:create", "project.timesheet", "create", "project"),
    ("project.timesheet:submit", "project.timesheet", "submit", "project"),
    ("project.timesheet:approve", "project.timesheet", "approve", "project"),
    ("project.resource:read", "project.resource", "read", "project"),
    ("project.resource:create", "project.resource", "create", "project"),
    ("project.resource:update", "project.resource", "update", "project"),
    ("project.budget:read", "project.budget", "read", "project"),
    ("project.budget:create", "project.budget", "create", "project"),
    ("project.budget:submit", "project.budget", "submit", "project"),
    ("project.budget:approve", "project.budget", "approve", "project"),
    ("project.cost:read", "project.cost", "read", "project"),
    ("project.cost:create", "project.cost", "create", "project"),
    ("project.cost:post", "project.cost", "post", "project"),
    ("project.issue:read", "project.issue", "read", "project"),
    ("project.issue:create", "project.issue", "create", "project"),
    ("project.issue:update", "project.issue", "update", "project"),
    ("project.risk:read", "project.risk", "read", "project"),
    ("project.risk:create", "project.risk", "create", "project"),
    ("project.risk:update", "project.risk", "update", "project"),
    ("project.change_request:read", "project.change_request", "read", "project"),
    ("project.change_request:create", "project.change_request", "create", "project"),
    ("project.change_request:submit", "project.change_request", "submit", "project"),
    ("project.change_request:approve", "project.change_request", "approve", "project"),
    ("project.document:read", "project.document", "read", "project"),
    ("project.document:create", "project.document", "create", "project"),
    ("project.document:update", "project.document", "update", "project"),
    ("project.comment:read", "project.comment", "read", "project"),
    ("project.comment:create", "project.comment", "create", "project"),
    ("project.comment:update", "project.comment", "update", "project"),
    ("project.report:read", "project.report", "read", "project"),
    ("project.report:export", "project.report", "export", "project"),
]

PROJECT_MEMBER_PERMISSIONS = list(
    dict.fromkeys(
        [
            p[0]
            for p in PROJECT_PERMISSIONS
            if p[2] in {"read", "create", "update", "submit", "complete"}
            and p[1]
            in {
                "project.task",
                "project.timesheet",
                "project.comment",
                "project.document",
                "project.issue",
                "project.project",
            }
        ]
    )
)

PROJECT_COORDINATOR_PERMISSIONS = list(
    dict.fromkeys(
        PROJECT_MEMBER_PERMISSIONS
        + [
            p[0]
            for p in PROJECT_PERMISSIONS
            if p[1] in {"project.phase", "project.milestone", "project.resource", "project.task"}
        ]
    )
)

PROJECT_MANAGER_PERMISSIONS = list(
    dict.fromkeys(
        PROJECT_COORDINATOR_PERMISSIONS
        + [
            "project.project:submit",
            "project.project:approve",
            "project.project:close",
            "project.task:approve",
            "project.timesheet:approve",
            "project.budget:submit",
            "project.budget:approve",
            "project.cost:create",
            "project.cost:post",
            "project.change_request:submit",
            "project.change_request:approve",
            "project.risk:create",
            "project.risk:update",
            "project.report:read",
            "project.report:export",
        ]
    )
)

PROJECT_ADMIN_PERMISSIONS = list(dict.fromkeys([p[0] for p in PROJECT_PERMISSIONS]))
''',
    )


def gen_api() -> None:
    w(
        PRJ / "dependencies.py",
        '''"""Project module dependencies."""

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
''',
    )

    schema_lines = [
        '"""Project Pydantic schemas."""',
        "",
        "from uuid import UUID",
        "",
        "from pydantic import BaseModel, ConfigDict",
        "",
        "",
        "class OrmModel(BaseModel):",
        "    model_config = ConfigDict(from_attributes=True)",
        "",
    ]
    for _, name, _, _, branch in ROUTE_SPECS:
        schema_lines += [
            "",
            f"class {name}Create(BaseModel):",
            "    company_id: UUID | None = None",
        ]
        if branch:
            schema_lines.append("    branch_id: UUID")
        schema_lines += [
            "    status: str | None = None",
            "",
            f"class {name}Update(BaseModel):",
            "    status: str | None = None",
            "    version: int | None = None",
            "",
            f"class {name}Response(OrmModel):",
            "    id: UUID",
            "    company_id: UUID",
            "    status: str",
            "    version: int",
        ]
    schema_lines += [
        "",
        "class ProjectCostPostRequest(BaseModel):",
        "    debit_account_id: UUID",
        "    credit_account_id: UUID",
        "    fiscal_year_id: UUID | None = None",
    ]
    w(PRJ / "schemas.py", "\n".join(schema_lines) + "\n")

    router_imports = [
        "from typing import Annotated",
        "from uuid import UUID",
        "",
        "from fastapi import APIRouter, Depends",
        "from sqlalchemy.orm import Session",
        "",
        "from shared.schemas import APIResponse",
        "from modules.project.dependencies import (",
        "    PaginationParams,",
        "    extract_update_fields,",
        "    get_db,",
        "    get_pagination,",
        "    paginate,",
        "    require_permission,",
        ")",
        "from modules.foundation.domain.value_objects import TenantContext",
        "from modules.project.schemas import (",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        router_imports.append(f"    {name}Create,")
        router_imports.append(f"    {name}Response,")
        router_imports.append(f"    {name}Update,")
    router_imports += [
        "    ProjectCostPostRequest,",
        ")",
        "from modules.project.service import (",
    ]
    for _, _, svc, _, _ in ROUTE_SPECS:
        router_imports.append(f"    {svc},")
    router_imports.append(")")

    router_defs: list[str] = []
    route_handlers: list[str] = []
    for prefix, name, svc, perm, branch in ROUTE_SPECS:
        rname = f"{prefix.replace('-', '_')}_router"
        router_defs += ["", f'{rname} = APIRouter(prefix="/{prefix}", tags=["Project â€” {name}"])']
        list_create_kw = ""
        if branch:
            create_call = f"{svc}(db).create(ctx, branch_id=body.branch_id, **body.model_dump(exclude={{'branch_id'}}, exclude_none=True))"
        else:
            create_call = f"{svc}(db).create(ctx, **body.model_dump(exclude_none=True))"
        route_handlers += [
            "",
            f"@{rname}.get(\"\", response_model=APIResponse[list[{name}Response]])",
            f"def list_{prefix.replace('-', '_')}(",
            "    ctx: Annotated[TenantContext, Depends(require_permission(\"" + perm + ":read\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "    pagination: Annotated[PaginationParams, Depends(get_pagination)],",
            "    company_id: UUID | None = None,",
            "):",
            f"    items = {svc}(db).list(ctx, company_id=company_id)",
            "    return APIResponse(message=\"OK\", data=paginate(items, pagination))",
            "",
            f"@{rname}.get(\"{{row_id}}\", response_model=APIResponse[{name}Response])",
            f"def get_{prefix.replace('-', '_')}(",
            "    row_id: UUID,",
            "    ctx: Annotated[TenantContext, Depends(require_permission(\"" + perm + ":read\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f"    return APIResponse(message=\"OK\", data={svc}(db).get(ctx, row_id))",
            "",
            f"@{rname}.post(\"\", response_model=APIResponse[{name}Response])",
            f"def create_{prefix.replace('-', '_')}(",
            f"    body: {name}Create,",
            "    ctx: Annotated[TenantContext, Depends(require_permission(\"" + perm + ":create\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f"    return APIResponse(message=\"Created\", data={create_call})",
            "",
            f"@{rname}.patch(\"{{row_id}}\", response_model=APIResponse[{name}Response])",
            f"def update_{prefix.replace('-', '_')}(",
            "    row_id: UUID,",
            f"    body: {name}Update,",
            "    ctx: Annotated[TenantContext, Depends(require_permission(\""
            + (perm + ":update" if perm != "project.report" else "project.report:export")
            + "\"))],",
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f"    return APIResponse(message=\"Updated\", data={svc}(db).update(ctx, row_id, **extract_update_fields(body)))",
        ]
        # lifecycle actions
        if svc == "ProjectService":
            for act, paction in [("submit", "submit"), ("approve", "approve"), ("close", "close")]:
                route_handlers += [
                    "",
                    f"@{rname}.post(\"{{row_id}}/{act}\", response_model=APIResponse[{name}Response])",
                    f"def {act}_{prefix.replace('-', '_')}(",
                    "    row_id: UUID,",
                    f'    ctx: Annotated[TenantContext, Depends(require_permission("project.project:{paction}"))],',
                    "    db: Annotated[Session, Depends(get_db)],",
                    "):",
                    f'    return APIResponse(message="{act.title()}", data={svc}(db).{act}(ctx, row_id))',
                ]
        if svc == "TaskService":
            for act, paction in [("submit", "update"), ("approve", "approve")]:
                route_handlers += [
                    "",
                    f"@{rname}.post(\"{{row_id}}/{act}\", response_model=APIResponse[{name}Response])",
                    f"def {act}_{prefix.replace('-', '_')}(",
                    "    row_id: UUID,",
                    f'    ctx: Annotated[TenantContext, Depends(require_permission("project.task:{paction}"))],',
                    "    db: Annotated[Session, Depends(get_db)],",
                    "):",
                    f'    return APIResponse(message="{act.title()}", data={svc}(db).{act}(ctx, row_id))',
                ]
        if svc == "TimesheetService":
            for act in ("submit", "approve"):
                route_handlers += [
                    "",
                    f"@{rname}.post(\"{{row_id}}/{act}\", response_model=APIResponse[{name}Response])",
                    f"def {act}_{prefix.replace('-', '_')}(",
                    "    row_id: UUID,",
                    f'    ctx: Annotated[TenantContext, Depends(require_permission("project.timesheet:{act}"))],',
                    "    db: Annotated[Session, Depends(get_db)],",
                    "):",
                    f'    return APIResponse(message="{act.title()}", data={svc}(db).{act}(ctx, row_id))',
                ]
        if svc == "BudgetService":
            for act in ("submit", "approve"):
                route_handlers += [
                    "",
                    f"@{rname}.post(\"{{row_id}}/{act}\", response_model=APIResponse[{name}Response])",
                    f"def {act}_{prefix.replace('-', '_')}(",
                    "    row_id: UUID,",
                    f'    ctx: Annotated[TenantContext, Depends(require_permission("project.budget:{act}"))],',
                    "    db: Annotated[Session, Depends(get_db)],",
                    "):",
                    f'    return APIResponse(message="{act.title()}", data={svc}(db).{act}(ctx, row_id))',
                ]
        if svc == "ChangeRequestService":
            for act in ("submit", "approve"):
                route_handlers += [
                    "",
                    f"@{rname}.post(\"{{row_id}}/{act}\", response_model=APIResponse[{name}Response])",
                    f"def {act}_{prefix.replace('-', '_')}(",
                    "    row_id: UUID,",
                    f'    ctx: Annotated[TenantContext, Depends(require_permission("project.change_request:{act}"))],',
                    "    db: Annotated[Session, Depends(get_db)],",
                    "):",
                    f'    return APIResponse(message="{act.title()}", data={svc}(db).{act}(ctx, row_id))',
                ]
        if svc == "CostService":
            route_handlers += [
                "",
                f"@{rname}.post(\"{{row_id}}/post\", response_model=APIResponse[{name}Response])",
                f"def post_{prefix.replace('-', '_')}(",
                "    row_id: UUID,",
                "    body: ProjectCostPostRequest,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("project.cost:post"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    return APIResponse(message=\"Posted\", data={svc}(db).post(",
                "        ctx, row_id, body.debit_account_id, body.credit_account_id, body.fiscal_year_id",
                "    ))",
            ]

    w(
        PRJ / "routers" / "__init__.py",
        '"""Project REST routers."""\n\n'
        + "\n".join(router_imports)
        + "\n".join(router_defs)
        + "\n".join(route_handlers)
        + "\n",
    )

    include_lines = [f"    {prefix.replace('-', '_')}_router," for prefix, _, _, _, _ in ROUTE_SPECS]
    w(
        PRJ / "router.py",
        '''"""Project module router aggregation."""

from fastapi import APIRouter

from modules.project.routers import (
'''
        + "\n".join(include_lines)
        + '''
)

project_router = APIRouter(prefix="/projects")
'''
        + "\n".join(
            f"project_router.include_router({prefix.replace('-', '_')}_router)"
            for prefix, _, _, _, _ in ROUTE_SPECS
        )
        + "\n",
    )


def gen_tasks_tests() -> None:
    w(
        PRJ / "tasks.py",
        '''"""Project Celery tasks."""

from workers.celery_app import celery_app


@celery_app.task(name="project.deadline_reminders")
def deadline_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProjectTask

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProjectTask).where(
                    PrjProjectTask.is_deleted.is_(False),
                    PrjProjectTask.status.in_(["open", "in_progress"]),
                )
            ).all()
        )
        return {"status": "ok", "open_tasks": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.timesheet_reminders")
def timesheet_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjTimesheet

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjTimesheet).where(
                    PrjTimesheet.is_deleted.is_(False),
                    PrjTimesheet.status == "draft",
                )
            ).all()
        )
        return {"status": "ok", "draft_timesheets": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.budget_threshold_alerts")
def budget_threshold_alerts() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProjectBudget

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProjectBudget).where(
                    PrjProjectBudget.is_deleted.is_(False),
                    PrjProjectBudget.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_budgets": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.risk_review_notifications")
def risk_review_notifications() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProjectRisk

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProjectRisk).where(
                    PrjProjectRisk.is_deleted.is_(False),
                    PrjProjectRisk.status.in_(["identified", "mitigating"]),
                )
            ).all()
        )
        return {"status": "ok", "open_risks": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.project_health_refresh")
def project_health_refresh() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProject

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProject).where(
                    PrjProject.is_deleted.is_(False),
                    PrjProject.status == "in_progress",
                )
            ).all()
        )
        return {"status": "ok", "in_progress_projects": len(rows)}
    finally:
        db.close()


@celery_app.task(name="project.retry_finance_posting")
def retry_finance_posting() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.project.models import PrjProjectCost

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(PrjProjectCost).where(
                    PrjProjectCost.is_deleted.is_(False),
                    PrjProjectCost.status == "failed",
                )
            ).all()
        )
        return {"status": "ok", "failed_costs": len(rows)}
    finally:
        db.close()
''',
    )

    w(
        TESTS / "unit" / "project" / "test_project_engines.py",
        '''"""Unit tests for project engines."""

from types import SimpleNamespace

from modules.project.service.engines import (
    ChangeRequestEngine,
    ProjectBudgetEngine,
    ProjectCostEngine,
    ProjectEngine,
    ProjectTaskEngine,
    TimesheetEngine,
)


def test_project_lifecycle():
    engine = ProjectEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"
    engine.start(row)
    assert row.status == "in_progress"
    engine.complete(row)
    assert row.status == "completed"
    engine.close(row)
    assert row.status == "closed"


def test_task_submit_approve():
    engine = ProjectTaskEngine()
    row = SimpleNamespace(status="open")
    engine.submit(row)
    engine.approve(row)
    assert row.status == "approved"


def test_timesheet_submit_approve():
    engine = TimesheetEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    assert row.status == "approved"


def test_budget_and_change_and_cost():
    budget = ProjectBudgetEngine()
    brow = SimpleNamespace(status="draft")
    budget.submit(brow)
    budget.approve(brow)
    assert brow.status == "approved"

    change = ChangeRequestEngine()
    crow = SimpleNamespace(status="draft")
    change.submit(crow)
    change.approve(crow)
    assert crow.status == "approved"

    cost = ProjectCostEngine()
    cost_row = SimpleNamespace(status="draft")
    cost.post(cost_row)
    assert cost_row.status == "posted"
''',
    )

    w(
        TESTS / "unit" / "project" / "test_project_tasks.py",
        '''"""Unit tests for project Celery tasks."""

from modules.project import tasks as project_tasks


def test_project_task_names_registered():
    assert project_tasks.deadline_reminders.name == "project.deadline_reminders"
    assert project_tasks.timesheet_reminders.name == "project.timesheet_reminders"
    assert project_tasks.budget_threshold_alerts.name == "project.budget_threshold_alerts"
    assert project_tasks.risk_review_notifications.name == "project.risk_review_notifications"
    assert project_tasks.project_health_refresh.name == "project.project_health_refresh"
    assert project_tasks.retry_finance_posting.name == "project.retry_finance_posting"
''',
    )

    w(
        TESTS / "security" / "project" / "test_project_permissions.py",
        '''"""Project RBAC permission tests."""

from modules.project.permissions import (
    PROJECT_ADMIN_PERMISSIONS,
    PROJECT_COORDINATOR_PERMISSIONS,
    PROJECT_MANAGER_PERMISSIONS,
    PROJECT_MEMBER_PERMISSIONS,
    PROJECT_PERMISSIONS,
)


def test_project_permissions_defined():
    assert len(PROJECT_PERMISSIONS) >= 40
    assert "project.project:close" in [p[0] for p in PROJECT_PERMISSIONS]
    assert "project.cost:post" in [p[0] for p in PROJECT_PERMISSIONS]


def test_project_roles():
    assert PROJECT_MEMBER_PERMISSIONS
    assert PROJECT_COORDINATOR_PERMISSIONS
    assert PROJECT_MANAGER_PERMISSIONS
    assert PROJECT_ADMIN_PERMISSIONS
    assert "project.project:approve" in PROJECT_MANAGER_PERMISSIONS
    assert "project.cost:post" in PROJECT_ADMIN_PERMISSIONS
''',
    )

    w(
        TESTS / "integration" / "project" / "test_project_module_import.py",
        '''"""Integration smoke: Project module imports and router mount."""

from modules.project.models import PrjProject, PrjProjectCost, PrjProjectTask
from modules.project.router import project_router
from modules.project.service import CostService, ProjectApplicationService, ProjectService
from modules.project.service.engines import ProjectEngine, ProjectCostEngine


def test_project_models_importable():
    assert PrjProject.__tablename__ == "prj_project"
    assert PrjProjectTask.__tablename__ == "prj_project_task"
    assert PrjProjectCost.__tablename__ == "prj_project_cost"


def test_project_router_mounted():
    assert project_router.prefix == "/projects"
    assert len(project_router.routes) > 20


def test_project_services_and_engines_importable():
    assert ProjectApplicationService is not None
    assert ProjectService is not None
    assert CostService is not None
    assert ProjectEngine is not None
    assert ProjectCostEngine is not None
''',
    )


def gen_seeds() -> None:
    w(
        ALEMBIC / "0243_seed_project_permissions.py",
        '''"""Seed project permissions and roles."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.project.permissions import (
    PROJECT_ADMIN_PERMISSIONS,
    PROJECT_COORDINATOR_PERMISSIONS,
    PROJECT_MANAGER_PERMISSIONS,
    PROJECT_MEMBER_PERMISSIONS,
    PROJECT_PERMISSIONS,
)

revision: str = "0243_seed_project_permissions"
down_revision: str | None = "0242_prj_project_report"
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
    ("PROJECT_MANAGER", "Project Manager", PROJECT_MANAGER_PERMISSIONS),
    ("PROJECT_COORDINATOR", "Project Coordinator", PROJECT_COORDINATOR_PERMISSIONS),
    ("PROJECT_MEMBER", "Project Member", PROJECT_MEMBER_PERMISSIONS),
    ("PROJECT_ADMIN", "Project Admin", PROJECT_ADMIN_PERMISSIONS),
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
    for code, resource, action, module in PROJECT_PERMISSIONS:
        perm_ids[code] = _ensure_permission(conn, now, code, resource, action, module)
    tenants = conn.execute(
        sa.text("SELECT id FROM foundation.sec_tenant WHERE is_deleted = false")
    ).fetchall()
    for (tenant_id,) in tenants:
        tid = str(tenant_id)
        for role_code, role_name, perms in ROLE_SPECS:
            role_id = _ensure_role(conn, now, tid, role_code, role_name)
            for perm_code in perms:
                _grant(conn, now, tid, role_id, perm_ids[perm_code])


def downgrade() -> None:
    conn = op.get_bind()
    for role_code, _, _ in reversed(ROLE_SPECS):
        conn.execute(
            sa.text(
                "DELETE FROM foundation.sec_role WHERE role_code = :code AND is_system_role = true"
            ),
            {"code": role_code},
        )
    for code, _, _, _ in PROJECT_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        )
''',
    )

    w(
        ALEMBIC / "0244_seed_project_workflows.py",
        '''"""Seed project workflow definitions per ERD_14."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0244_seed_project_workflows"
down_revision: str | None = "0243_seed_project_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "PRJ_PROJECT_APPROVAL",
        "Project Approval",
        "prj_project",
        [
            (1, "PROJECT_MANAGER", "Project Manager Submit", "role"),
            (2, "PROJECT_ADMIN", "Department / Admin Approval", "role"),
            (3, "PROJECT_ADMIN", "Finance Review", "role"),
        ],
    ),
    (
        "PRJ_TASK_APPROVAL",
        "Project Task Approval",
        "prj_project_task",
        [
            (1, "PROJECT_MEMBER", "Assignee / Coordinator Submit", "role"),
            (2, "PROJECT_MANAGER", "Project Manager Approval", "role"),
        ],
    ),
    (
        "PRJ_BUDGET_APPROVAL",
        "Project Budget Approval",
        "prj_project_budget",
        [
            (1, "PROJECT_MANAGER", "Project Manager Submit", "role"),
            (2, "PROJECT_ADMIN", "Finance Approval", "role"),
        ],
    ),
    (
        "PRJ_CHANGE_REQUEST_APPROVAL",
        "Change Request Approval",
        "prj_change_request",
        [
            (1, "PROJECT_MEMBER", "Requestor Submit", "role"),
            (2, "PROJECT_MANAGER", "Project Manager Approval", "role"),
            (3, "PROJECT_ADMIN", "Sponsor / Finance Review", "role"),
        ],
    ),
    (
        "PRJ_PROJECT_CLOSURE",
        "Project Closure",
        "prj_project",
        [
            (1, "PROJECT_MANAGER", "Project Manager Close Request", "role"),
            (2, "PROJECT_ADMIN", "Project Admin Approval", "role"),
            (3, "PROJECT_ADMIN", "Finance Review", "role"),
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
                        VALUES (:id, :tid, :code, :name, 'project', :doc, 1, true, :now, :now)
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
                        WHERE workflow_id = :wid AND step_order = :ord
                        """
                    ),
                    {"wid": wf_id, "ord": step_order},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, workflow_id, step_order, step_code, step_name,
                         approver_type, is_parallel, created_at, updated_at)
                        VALUES (:id, :tid, :wid, :ord, :code, :name, :atype, false, :now, :now)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wid": wf_id,
                        "ord": step_order,
                        "code": step_code,
                        "name": step_name,
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
                DELETE FROM foundation.wf_step
                WHERE workflow_id IN (
                    SELECT id FROM foundation.wf_definition WHERE workflow_code = :code
                )
                """
            ),
            {"code": workflow_code},
        )
        conn.execute(
            sa.text("DELETE FROM foundation.wf_definition WHERE workflow_code = :code"),
            {"code": workflow_code},
        )
''',
    )


def gen_wiring() -> None:
    patch_file(
        SHARED / "router.py",
        "from modules.recruitment.router import recruitment_router\n",
        "from modules.recruitment.router import recruitment_router\n"
        "from modules.project.router import project_router\n",
    )
    patch_file(
        SHARED / "router.py",
        "api_v1_router.include_router(recruitment_router)\n",
        "api_v1_router.include_router(recruitment_router)\n"
        "api_v1_router.include_router(project_router)\n",
    )
    patch_file(
        ROOT / "alembic" / "env.py",
        "import modules.recruitment.models  # noqa: F401 â€” register ORM metadata\n",
        "import modules.recruitment.models  # noqa: F401 â€” register ORM metadata\n"
        "import modules.project.models  # noqa: F401 â€” register ORM metadata\n",
    )
    patch_file(
        ROOT / "src" / "workers" / "celery_app.py",
        '        "modules.recruitment",\n',
        '        "modules.recruitment",\n        "modules.project",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '    "modules.recruitment.*",\n',
        '    "modules.recruitment.*",\n    "modules.project.*",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '"src/modules/recruitment/domain/enums.py" = ["UP042"]\n',
        '"src/modules/recruitment/domain/enums.py" = ["UP042"]\n'
        '"src/modules/project/**" = ["E501", "SIM102"]\n'
        '"src/modules/project/domain/enums.py" = ["UP042"]\n',
    )


def main() -> None:
    gen_scaffold()
    gen_domain()
    gen_models()
    gen_migrations()
    gen_repos()
    gen_engines()
    gen_services()
    gen_adapters()
    gen_permissions()
    gen_api()
    gen_tasks_tests()
    gen_seeds()
    gen_wiring()
    print(f"OK project module generated â€” {len(FILES_WRITTEN)} files")
    print("Alembic head revision: 0244_seed_project_workflows")


if __name__ == "__main__":
    main()

