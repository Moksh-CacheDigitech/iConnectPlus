"""Generate Sprint 16 Service Management module. Run from apps/api:
.venv\\Scripts\\python.exe scripts/_gen_service_module.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SVC = SRC / "modules" / "service"
ALEMBIC = ROOT / "alembic" / "versions"
TESTS = SRC / "tests"
SHARED = SRC / "shared"

FILES_WRITTEN: list[Path] = []

OPT_BRANCH = """
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
"""

WF_FIELDS = """
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
"""


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


# table_key, ORM class, Repo/Engine stem, branch_scoped
TABLES: list[tuple[str, str, str, bool]] = [
    ("service_category", "SvcServiceCategory", "ServiceCategory", False),
    ("service_request", "SvcServiceRequest", "ServiceRequest", True),
    ("service_ticket", "SvcServiceTicket", "ServiceTicket", True),
    ("service_assignment", "SvcServiceAssignment", "ServiceAssignment", True),
    ("service_schedule", "SvcServiceSchedule", "ServiceSchedule", True),
    ("service_work_order", "SvcServiceWorkOrder", "ServiceWorkOrder", True),
    ("service_task", "SvcServiceTask", "ServiceTask", False),
    ("service_checklist", "SvcServiceChecklist", "ServiceChecklist", False),
    ("service_visit", "SvcServiceVisit", "ServiceVisit", True),
    ("service_material", "SvcServiceMaterial", "ServiceMaterial", False),
    ("service_time_entry", "SvcServiceTimeEntry", "ServiceTimeEntry", False),
    ("service_expense", "SvcServiceExpense", "ServiceExpense", True),
    ("service_sla", "SvcServiceSla", "ServiceSla", False),
    ("service_escalation", "SvcServiceEscalation", "ServiceEscalation", True),
    ("service_feedback", "SvcServiceFeedback", "ServiceFeedback", False),
    ("service_resolution", "SvcServiceResolution", "ServiceResolution", True),
    ("service_document", "SvcServiceDocument", "ServiceDocument", False),
    ("service_notification", "SvcServiceNotification", "ServiceNotification", False),
    ("service_contract", "SvcServiceContract", "ServiceContract", True),
    ("service_report", "SvcServiceReport", "ServiceReport", False),
]

CLASS_MAP = {t[0]: t[1] for t in TABLES}

MIGRATIONS: list[tuple[str, str | list[str], str]] = [
    ("0267_create_service_schema", "schema", "0266_seed_asset_workflows"),
    ("0268_svc_service_category", "service_category", "0267_create_service_schema"),
    ("0269_svc_service_request", "service_request", "0268_svc_service_category"),
    ("0270_svc_service_ticket", "service_ticket", "0269_svc_service_request"),
    ("0271_svc_service_assignment", "service_assignment", "0270_svc_service_ticket"),
    ("0272_svc_service_schedule", "service_schedule", "0271_svc_service_assignment"),
    ("0273_svc_service_work_order", "service_work_order", "0272_svc_service_schedule"),
    ("0274_svc_service_task", "service_task", "0273_svc_service_work_order"),
    ("0275_svc_service_checklist", "service_checklist", "0274_svc_service_task"),
    ("0276_svc_service_visit", "service_visit", "0275_svc_service_checklist"),
    ("0277_svc_service_material", "service_material", "0276_svc_service_visit"),
    ("0278_svc_time_expense", ["service_time_entry", "service_expense"], "0277_svc_service_material"),
    ("0279_svc_service_sla", "service_sla", "0278_svc_time_expense"),
    ("0280_svc_service_escalation", "service_escalation", "0279_svc_service_sla"),
    ("0281_svc_service_feedback", "service_feedback", "0280_svc_service_escalation"),
    ("0282_svc_service_resolution", "service_resolution", "0281_svc_service_feedback"),
    ("0283_svc_service_document", "service_document", "0282_svc_service_resolution"),
    ("0284_svc_service_notification", "service_notification", "0283_svc_service_document"),
    ("0285_svc_service_contract", "service_contract", "0284_svc_service_notification"),
    ("0286_svc_service_report", "service_report", "0285_svc_service_contract"),
    ("0287_seed_service_permissions", "seed_perms", "0286_svc_service_report"),
    ("0288_seed_service_workflows", "seed_wf", "0287_seed_service_permissions"),
]

ROUTE_SPECS: list[tuple[str, str, str, str, bool]] = [
    ("service-categories", "ServiceCategory", "ServiceCategoryService", "service.category", False),
    ("service-requests", "ServiceRequest", "ServiceRequestService", "service.request", True),
    ("service-tickets", "ServiceTicket", "ServiceTicketService", "service.ticket", True),
    ("service-assignments", "ServiceAssignment", "ServiceAssignmentService", "service.assignment", True),
    ("service-schedules", "ServiceSchedule", "ServiceScheduleService", "service.schedule", True),
    ("work-orders", "WorkOrder", "WorkOrderService", "service.work_order", True),
    ("service-tasks", "ServiceTask", "ServiceTaskService", "service.task", False),
    ("service-checklists", "ServiceChecklist", "ServiceChecklistService", "service.checklist", False),
    ("service-visits", "ServiceVisit", "ServiceVisitService", "service.visit", True),
    ("service-materials", "ServiceMaterial", "ServiceMaterialService", "service.material", False),
    ("time-entries", "ServiceTimeEntry", "ServiceTimeEntryService", "service.time_entry", False),
    ("service-expenses", "ServiceExpense", "ServiceExpenseService", "service.expense", True),
    ("service-slas", "ServiceSla", "ServiceSLAService", "service.sla", False),
    ("service-escalations", "ServiceEscalation", "ServiceEscalationService", "service.escalation", True),
    ("service-feedback", "ServiceFeedback", "ServiceFeedbackService", "service.feedback", False),
    ("service-resolutions", "ServiceResolution", "ServiceResolutionService", "service.resolution", True),
    ("service-documents", "ServiceDocument", "ServiceDocumentService", "service.document", False),
    ("service-notifications", "ServiceNotification", "ServiceNotificationService", "service.notification", False),
    ("service-contracts", "ServiceContract", "ServiceContractService", "service.contract", True),
    ("reports", "ServiceReport", "ServiceReportService", "service.report", False),
]

# ---------------------------------------------------------------------------
# MODEL BODIES
# ---------------------------------------------------------------------------

MODELS: dict[str, str] = {}

MODELS["service_category"] = f'''"""Service category ORM per ERD_16 section 6.1."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcMasterMixin


class SvcServiceCategory(Base, *SvcMasterMixin):
    __tablename__ = "svc_service_category"
    __table_args__ = (
        UniqueConstraint("company_id", "category_code", name="uk_svc_service_category_code"),
        CheckConstraint(
            "default_priority IN ('low','medium','high','critical')",
            name="ck_svc_service_category_priority",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_svc_service_category_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    category_code: Mapped[str] = mapped_column(String(50), nullable=False)
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    default_sla_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_sla.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_category_default_sla",
        ),
        nullable=True,
        index=True,
    )
    is_billable_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["service_request"] = f'''"""Service request ORM per ERD_16 section 6.2."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceRequest(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_request"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_request_doc"),
        CheckConstraint(
            "service_type IN ('preventive','corrective','breakdown','installation','inspection','other')",
            name="ck_svc_service_request_type",
        ),
        CheckConstraint(
            "priority IN ('low','medium','high','critical')",
            name="ck_svc_service_request_priority",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','new','assigned','in_progress',"
            "'resolved','closed','cancelled')",
            name="ck_svc_service_request_status",
        ),
        CheckConstraint(
            "sla_status IS NULL OR sla_status IN ('within_sla','at_risk','breached')",
            name="ck_svc_service_request_sla_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    category_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_category.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    requested_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    contract_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_contract.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_request_contract",
        ),
        nullable=True,
        index=True,
    )
    service_type: Mapped[str] = mapped_column(String(40), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    channel: Mapped[str | None] = mapped_column(String(40), nullable=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    master_asset_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_asset.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    asset_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    maintenance_plan_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    crm_opportunity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    crm_customer_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    project_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    sla_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_sla.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_request_sla",
        ),
        nullable=True,
        index=True,
    )
    sla_status: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["service_ticket"] = f'''"""Service ticket ORM per ERD_16 section 6.3."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceTicket(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_ticket"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_ticket_doc"),
        CheckConstraint(
            "ticket_type IN ('incident','request','problem','change')",
            name="ck_svc_service_ticket_type",
        ),
        CheckConstraint(
            "status IN ('open','pending','in_progress','resolved','closed','cancelled')",
            name="ck_svc_service_ticket_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    ticket_type: Mapped[str] = mapped_column(String(40), nullable=False, default="incident")
    queue_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
'''

MODELS["service_assignment"] = f'''"""Service assignment ORM per ERD_16 section 6.4."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceAssignment(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_assignment"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_assignment_doc"),
        CheckConstraint(
            "role_on_job IN ('primary','secondary','observer')",
            name="ck_svc_service_assignment_role",
        ),
        CheckConstraint(
            "status IN ('draft','active','completed','cancelled')",
            name="ck_svc_service_assignment_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_ticket.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_work_order.id",
            ondelete="RESTRICT",
            use_alter=True,
            name="fk_svc_assignment_work_order",
        ),
        nullable=True,
        index=True,
    )
    technician_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role_on_job: Mapped[str] = mapped_column(String(30), nullable=False, default="primary")
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    unassigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["service_schedule"] = f'''"""Service schedule ORM per ERD_16 section 6.5."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceSchedule(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_schedule"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_schedule_doc"),
        CheckConstraint(
            "status IN ('planned','confirmed','in_progress','completed','cancelled')",
            name="ck_svc_service_schedule_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_work_order.id",
            ondelete="RESTRICT",
            use_alter=True,
            name="fk_svc_schedule_work_order",
        ),
        nullable=False,
        index=True,
    )
    technician_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    planned_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    planned_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
'''

MODELS["service_work_order"] = f'''"""Service work order ORM per ERD_16 section 6.6."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceWorkOrder(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_work_order"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_work_order_doc"),
        CheckConstraint(
            "work_order_type IN ('preventive','corrective','breakdown','installation','other')",
            name="ck_svc_service_work_order_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','assigned','in_progress',"
            "'completed','closed','cancelled')",
            name="ck_svc_service_work_order_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_ticket.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    work_order_type: Mapped[str] = mapped_column(String(40), nullable=False)
    primary_technician_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    asset_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    maintenance_plan_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    inventory_issue_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    inventory_receipt_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    purchase_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    project_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    production_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    quality_inspection_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    estimated_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    actual_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["service_task"] = f'''"""Service task ORM per ERD_16 section 6.7."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceTask(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_task"
    __table_args__ = (
        UniqueConstraint("work_order_id", "task_code", name="uk_svc_service_task_code"),
        CheckConstraint(
            "status IN ('pending','in_progress','completed','cancelled','blocked')",
            name="ck_svc_service_task_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    task_code: Mapped[str] = mapped_column(String(50), nullable=False)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    assignee_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    planned_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    actual_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
'''

MODELS["service_checklist"] = f'''"""Service checklist ORM per ERD_16 section 6.8."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceChecklist(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_checklist"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','completed','cancelled')",
            name="ck_svc_service_checklist_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    visit_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_visit.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_checklist_visit",
        ),
        nullable=True,
        index=True,
    )
    task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_task.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    checklist_code: Mapped[str] = mapped_column(String(50), nullable=False)
    checklist_name: Mapped[str] = mapped_column(String(255), nullable=False)
    items_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["service_visit"] = f'''"""Service visit ORM per ERD_16 section 6.9."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceVisit(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_visit"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_visit_doc"),
        CheckConstraint(
            "status IN ('planned','checked_in','completed','cancelled')",
            name="ck_svc_service_visit_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    technician_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    visit_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    visit_ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    site_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    geo_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    customer_signoff_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
'''

MODELS["service_material"] = f'''"""Service material ORM per ERD_16 section 6.10."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceMaterial(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_material"
    __table_args__ = (
        CheckConstraint(
            "status IN ('reserved','issued','returned','cancelled')",
            name="ck_svc_service_material_status",
        ),
        CheckConstraint("quantity >= 0", name="ck_svc_service_material_qty"),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    line_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    inventory_issue_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="reserved", index=True)
'''

# Fix missing String import in service_material
MODELS["service_material"] = MODELS["service_material"].replace(
    "from sqlalchemy import CheckConstraint, ForeignKey, Numeric",
    "from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String",
)

MODELS["service_time_entry"] = f'''"""Service time entry ORM per ERD_16 section 6.11."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceTimeEntry(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_time_entry"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','submitted','approved','void')",
            name="ck_svc_service_time_entry_status",
        ),
        CheckConstraint("hours >= 0", name="ck_svc_service_time_entry_hours"),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_task.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    visit_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_visit.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_billable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    labor_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["service_expense"] = f'''"""Service expense ORM per ERD_16 section 6.12."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceExpense(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_expense"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_expense_doc"),
        CheckConstraint(
            "expense_type IN ('travel','lodging','meal','other','material_surcharge')",
            name="ck_svc_service_expense_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','posted','cancelled')",
            name="ck_svc_service_expense_status",
        ),
        CheckConstraint("amount >= 0", name="ck_svc_service_expense_amount"),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    expense_type: Mapped[str] = mapped_column(String(40), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    incurred_on: Mapped[date] = mapped_column(Date, nullable=False)
    employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    is_billable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

MODELS["service_sla"] = f'''"""Service SLA ORM per ERD_16 section 6.13."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceSla(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_sla"
    __table_args__ = (
        UniqueConstraint("company_id", "sla_code", name="uk_svc_service_sla_code"),
        CheckConstraint(
            "priority IN ('low','medium','high','critical')",
            name="ck_svc_service_sla_priority",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_svc_service_sla_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    sla_code: Mapped[str] = mapped_column(String(50), nullable=False)
    sla_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_contract.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_sla_contract",
        ),
        nullable=True,
        index=True,
    )
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    response_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    business_hours_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["service_escalation"] = f'''"""Service escalation ORM per ERD_16 section 6.14."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceEscalation(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_escalation"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_escalation_doc"),
        CheckConstraint(
            "reason_code IN ('sla_at_risk','sla_breached','customer_complaint','management')",
            name="ck_svc_service_escalation_reason",
        ),
        CheckConstraint(
            "status IN ('open','acknowledged','resolved','cancelled')",
            name="ck_svc_service_escalation_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_ticket.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    sla_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_sla.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    escalation_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    reason_code: Mapped[str] = mapped_column(String(40), nullable=False)
    escalated_to_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
{WF_FIELDS}
'''

MODELS["service_feedback"] = f'''"""Service feedback ORM per ERD_16 section 6.15."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceFeedback(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_feedback"
    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_svc_service_feedback_rating"),
        CheckConstraint(
            "status IN ('captured','reviewed','archived')",
            name="ck_svc_service_feedback_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="captured", index=True)
'''

MODELS["service_resolution"] = f'''"""Service resolution ORM per ERD_16 section 6.16."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceResolution(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_resolution"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_resolution_doc"),
        CheckConstraint(
            "resolution_code IN ('fixed','workaround','duplicate','cannot_reproduce','other')",
            name="ck_svc_service_resolution_code",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','completed','cancelled')",
            name="ck_svc_service_resolution_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_ticket.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    resolution_code: Mapped[str] = mapped_column(String(40), nullable=False)
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_time_fix: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["service_document"] = f'''"""Service document ORM per ERD_16 section 6.17."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceDocument(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_document"
    __table_args__ = (
        CheckConstraint(
            "document_type IN ('photo','report','contract','invoice_copy','customer_signoff','other')",
            name="ck_svc_service_document_type",
        ),
        CheckConstraint(
            "status IN ('active','superseded','archived')",
            name="ck_svc_service_document_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    contract_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_contract.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_document_contract",
        ),
        nullable=True,
        index=True,
    )
    visit_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_visit.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["service_notification"] = f'''"""Service notification ORM per ERD_16 section 6.18."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceNotification(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_notification"
    __table_args__ = (
        CheckConstraint(
            "delivery_status IN ('pending','sent','failed','read')",
            name="ck_svc_service_notification_delivery",
        ),
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_svc_service_notification_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    contract_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_contract.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_notification_contract",
        ),
        nullable=True,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(60), nullable=False)
    recipient_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    recipient_employee_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    recipient_customer_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
'''

MODELS["service_contract"] = f'''"""Service contract ORM per ERD_16 section 6.19."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceContract(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_contract"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_contract_doc"),
        CheckConstraint(
            "contract_type IN ('amc','warranty','support','managed_services')",
            name="ck_svc_service_contract_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','expired','cancelled')",
            name="ck_svc_service_contract_status",
        ),
        CheckConstraint("end_date >= start_date", name="ck_svc_service_contract_dates"),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    contract_type: Mapped[str] = mapped_column(String(40), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    coverage_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_sla_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_sla.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    crm_opportunity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
{WF_FIELDS}
'''

MODELS["service_report"] = f'''"""Service report ORM per ERD_16 section 6.20."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceReport(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_report"
    __table_args__ = (
        UniqueConstraint("company_id", "report_code", name="uk_svc_service_report_code"),
        CheckConstraint(
            "report_type IN ('request_volume','sla_compliance','technician_utilization',"
            "'first_time_fix','contract_coverage','backlog')",
            name="ck_svc_service_report_type",
        ),
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_svc_service_report_status",
        ),
        {{"schema": "service"}},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
{OPT_BRANCH}
    report_code: Mapped[str] = mapped_column(String(50), nullable=False)
    report_type: Mapped[str] = mapped_column(String(60), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_category.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
'''

ENGINE_FILE_MAP = {
    "ServiceCategory": "service_category",
    "ServiceRequest": "service_request",
    "ServiceTicket": "service_ticket",
    "ServiceAssignment": "service_assignment",
    "ServiceSchedule": "service_schedule",
    "ServiceWorkOrder": "service_work_order",
    "ServiceTask": "service_task",
    "ServiceChecklist": "service_checklist",
    "ServiceVisit": "service_visit",
    "ServiceMaterial": "service_material",
    "ServiceTimeEntry": "service_time_entry",
    "ServiceExpense": "service_expense",
    "ServiceSla": "service_sla",
    "ServiceEscalation": "service_escalation",
    "ServiceFeedback": "service_feedback",
    "ServiceResolution": "service_resolution",
    "ServiceDocument": "service_document",
    "ServiceNotification": "service_notification",
    "ServiceContract": "service_contract",
    "ServiceReport": "service_report",
}

ENGINE_IMPORTS = """
from modules.service.domain.enums import (
    ServiceAssignmentStatus,
    ServiceCategoryStatus,
    ServiceChecklistStatus,
    ServiceContractStatus,
    ServiceDocumentStatus,
    ServiceEscalationStatus,
    ServiceExpenseStatus,
    ServiceFeedbackStatus,
    ServiceMaterialStatus,
    ServiceNotificationStatus,
    ServiceReportStatus,
    ServiceRequestStatus,
    ServiceResolutionStatus,
    ServiceScheduleStatus,
    ServiceSlaStatus,
    ServiceTaskStatus,
    ServiceTicketStatus,
    ServiceTimeEntryStatus,
    ServiceVisitStatus,
    ServiceWorkOrderStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceAssignmentState,
    InvalidServiceCategoryState,
    InvalidServiceChecklistState,
    InvalidServiceContractState,
    InvalidServiceDocumentState,
    InvalidServiceEscalationState,
    InvalidServiceExpenseState,
    InvalidServiceFeedbackState,
    InvalidServiceMaterialState,
    InvalidServiceNotificationState,
    InvalidServiceReportState,
    InvalidServiceRequestState,
    InvalidServiceResolutionState,
    InvalidServiceScheduleState,
    InvalidServiceSlaState,
    InvalidServiceTaskState,
    InvalidServiceTicketState,
    InvalidServiceTimeEntryState,
    InvalidServiceVisitState,
    InvalidServiceWorkOrderState,
)
"""

ENGINE_BODIES: dict[str, str] = {
    "ServiceCategory": '''
class ServiceCategoryEngine:
    def activate(self, row) -> None:
        row.status = ServiceCategoryStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ServiceCategoryStatus.INACTIVE.value
''',
    "ServiceRequest": '''
class ServiceRequestEngine:
    def submit(self, row) -> None:
        if row.status != ServiceRequestStatus.DRAFT.value:
            raise InvalidServiceRequestState("Only draft requests can be submitted")
        row.status = ServiceRequestStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceRequestStatus.SUBMITTED.value:
            raise InvalidServiceRequestState("Only submitted requests can be approved")
        row.status = ServiceRequestStatus.APPROVED.value

    def assign(self, row) -> None:
        if row.status not in {ServiceRequestStatus.APPROVED.value, ServiceRequestStatus.NEW.value}:
            raise InvalidServiceRequestState("Request not assignable")
        row.status = ServiceRequestStatus.ASSIGNED.value

    def start(self, row) -> None:
        if row.status != ServiceRequestStatus.ASSIGNED.value:
            raise InvalidServiceRequestState("Only assigned requests can start")
        row.status = ServiceRequestStatus.IN_PROGRESS.value

    def resolve(self, row) -> None:
        if row.status != ServiceRequestStatus.IN_PROGRESS.value:
            raise InvalidServiceRequestState("Only in-progress requests can resolve")
        row.status = ServiceRequestStatus.RESOLVED.value

    def close(self, row) -> None:
        if row.status != ServiceRequestStatus.RESOLVED.value:
            raise InvalidServiceRequestState("Only resolved requests can close")
        row.status = ServiceRequestStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ServiceRequestStatus.CLOSED.value, ServiceRequestStatus.CANCELLED.value}:
            raise InvalidServiceRequestState("Request already terminal")
        row.status = ServiceRequestStatus.CANCELLED.value
''',
    "ServiceTicket": '''
class ServiceTicketEngine:
    def start(self, row) -> None:
        if row.status not in {ServiceTicketStatus.OPEN.value, ServiceTicketStatus.PENDING.value}:
            raise InvalidServiceTicketState("Ticket not startable")
        row.status = ServiceTicketStatus.IN_PROGRESS.value

    def resolve(self, row) -> None:
        if row.status != ServiceTicketStatus.IN_PROGRESS.value:
            raise InvalidServiceTicketState("Only in-progress tickets can resolve")
        row.status = ServiceTicketStatus.RESOLVED.value

    def close(self, row) -> None:
        row.status = ServiceTicketStatus.CLOSED.value

    def cancel(self, row) -> None:
        row.status = ServiceTicketStatus.CANCELLED.value
''',
    "ServiceAssignment": '''
class ServiceAssignmentEngine:
    def activate(self, row) -> None:
        if row.status != ServiceAssignmentStatus.DRAFT.value:
            raise InvalidServiceAssignmentState("Only draft assignments can activate")
        row.status = ServiceAssignmentStatus.ACTIVE.value

    def complete(self, row) -> None:
        if row.status != ServiceAssignmentStatus.ACTIVE.value:
            raise InvalidServiceAssignmentState("Only active assignments can complete")
        row.status = ServiceAssignmentStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceAssignmentStatus.CANCELLED.value
''',
    "ServiceSchedule": '''
class ServiceScheduleEngine:
    def confirm(self, row) -> None:
        if row.status != ServiceScheduleStatus.PLANNED.value:
            raise InvalidServiceScheduleState("Only planned schedules can confirm")
        row.status = ServiceScheduleStatus.CONFIRMED.value

    def start(self, row) -> None:
        if row.status not in {ServiceScheduleStatus.PLANNED.value, ServiceScheduleStatus.CONFIRMED.value}:
            raise InvalidServiceScheduleState("Schedule not startable")
        row.status = ServiceScheduleStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != ServiceScheduleStatus.IN_PROGRESS.value:
            raise InvalidServiceScheduleState("Only in-progress schedules can complete")
        row.status = ServiceScheduleStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceScheduleStatus.CANCELLED.value
''',
    "ServiceWorkOrder": '''
class ServiceWorkOrderEngine:
    def submit(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.DRAFT.value:
            raise InvalidServiceWorkOrderState("Only draft work orders can be submitted")
        row.status = ServiceWorkOrderStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.SUBMITTED.value:
            raise InvalidServiceWorkOrderState("Only submitted work orders can be approved")
        row.status = ServiceWorkOrderStatus.APPROVED.value

    def assign(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.APPROVED.value:
            raise InvalidServiceWorkOrderState("Only approved work orders can be assigned")
        row.status = ServiceWorkOrderStatus.ASSIGNED.value

    def start(self, row) -> None:
        if row.status not in {ServiceWorkOrderStatus.APPROVED.value, ServiceWorkOrderStatus.ASSIGNED.value}:
            raise InvalidServiceWorkOrderState("Work order not startable")
        row.status = ServiceWorkOrderStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.IN_PROGRESS.value:
            raise InvalidServiceWorkOrderState("Only in-progress work orders can complete")
        row.status = ServiceWorkOrderStatus.COMPLETED.value

    def close(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.COMPLETED.value:
            raise InvalidServiceWorkOrderState("Only completed work orders can close")
        row.status = ServiceWorkOrderStatus.CLOSED.value

    def cancel(self, row) -> None:
        row.status = ServiceWorkOrderStatus.CANCELLED.value
''',
    "ServiceTask": '''
class ServiceTaskEngine:
    def start(self, row) -> None:
        if row.status != ServiceTaskStatus.PENDING.value:
            raise InvalidServiceTaskState("Only pending tasks can start")
        row.status = ServiceTaskStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != ServiceTaskStatus.IN_PROGRESS.value:
            raise InvalidServiceTaskState("Only in-progress tasks can complete")
        row.status = ServiceTaskStatus.COMPLETED.value

    def block(self, row) -> None:
        row.status = ServiceTaskStatus.BLOCKED.value

    def cancel(self, row) -> None:
        row.status = ServiceTaskStatus.CANCELLED.value
''',
    "ServiceChecklist": '''
class ServiceChecklistEngine:
    def complete(self, row) -> None:
        if row.status != ServiceChecklistStatus.DRAFT.value:
            raise InvalidServiceChecklistState("Only draft checklists can complete")
        row.status = ServiceChecklistStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceChecklistStatus.CANCELLED.value
''',
    "ServiceVisit": '''
class ServiceVisitEngine:
    def check_in(self, row) -> None:
        if row.status != ServiceVisitStatus.PLANNED.value:
            raise InvalidServiceVisitState("Only planned visits can check in")
        row.status = ServiceVisitStatus.CHECKED_IN.value

    def complete(self, row) -> None:
        if row.status != ServiceVisitStatus.CHECKED_IN.value:
            raise InvalidServiceVisitState("Only checked-in visits can complete")
        row.status = ServiceVisitStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceVisitStatus.CANCELLED.value
''',
    "ServiceMaterial": '''
class ServiceMaterialEngine:
    def issue(self, row) -> None:
        if row.status != ServiceMaterialStatus.RESERVED.value:
            raise InvalidServiceMaterialState("Only reserved materials can be issued")
        row.status = ServiceMaterialStatus.ISSUED.value

    def return_material(self, row) -> None:
        if row.status != ServiceMaterialStatus.ISSUED.value:
            raise InvalidServiceMaterialState("Only issued materials can be returned")
        row.status = ServiceMaterialStatus.RETURNED.value

    def cancel(self, row) -> None:
        row.status = ServiceMaterialStatus.CANCELLED.value
''',
    "ServiceTimeEntry": '''
class ServiceTimeEntryEngine:
    def submit(self, row) -> None:
        if row.status != ServiceTimeEntryStatus.DRAFT.value:
            raise InvalidServiceTimeEntryState("Only draft time entries can be submitted")
        row.status = ServiceTimeEntryStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceTimeEntryStatus.SUBMITTED.value:
            raise InvalidServiceTimeEntryState("Only submitted time entries can be approved")
        row.status = ServiceTimeEntryStatus.APPROVED.value

    def void(self, row) -> None:
        row.status = ServiceTimeEntryStatus.VOID.value
''',
    "ServiceExpense": '''
class ServiceExpenseEngine:
    def submit(self, row) -> None:
        if row.status != ServiceExpenseStatus.DRAFT.value:
            raise InvalidServiceExpenseState("Only draft expenses can be submitted")
        row.status = ServiceExpenseStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceExpenseStatus.SUBMITTED.value:
            raise InvalidServiceExpenseState("Only submitted expenses can be approved")
        row.status = ServiceExpenseStatus.APPROVED.value

    def post(self, row) -> None:
        if row.status != ServiceExpenseStatus.APPROVED.value:
            raise InvalidServiceExpenseState("Only approved expenses can be posted")
        row.status = ServiceExpenseStatus.POSTED.value

    def cancel(self, row) -> None:
        if row.status == ServiceExpenseStatus.POSTED.value:
            raise InvalidServiceExpenseState("Posted expenses cannot be cancelled")
        row.status = ServiceExpenseStatus.CANCELLED.value
''',
    "ServiceSla": '''
class ServiceSlaEngine:
    def activate(self, row) -> None:
        row.status = ServiceSlaStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ServiceSlaStatus.INACTIVE.value
''',
    "ServiceEscalation": '''
class ServiceEscalationEngine:
    def escalate(self, row) -> None:
        if row.status != ServiceEscalationStatus.OPEN.value:
            raise InvalidServiceEscalationState("Only open escalations can escalate further")
        row.escalation_level = int(row.escalation_level or 1) + 1

    def acknowledge(self, row) -> None:
        if row.status != ServiceEscalationStatus.OPEN.value:
            raise InvalidServiceEscalationState("Only open escalations can be acknowledged")
        row.status = ServiceEscalationStatus.ACKNOWLEDGED.value

    def resolve(self, row) -> None:
        if row.status not in {ServiceEscalationStatus.OPEN.value, ServiceEscalationStatus.ACKNOWLEDGED.value}:
            raise InvalidServiceEscalationState("Escalation not resolvable")
        row.status = ServiceEscalationStatus.RESOLVED.value

    def cancel(self, row) -> None:
        row.status = ServiceEscalationStatus.CANCELLED.value
''',
    "ServiceFeedback": '''
class ServiceFeedbackEngine:
    def review(self, row) -> None:
        if row.status != ServiceFeedbackStatus.CAPTURED.value:
            raise InvalidServiceFeedbackState("Only captured feedback can be reviewed")
        row.status = ServiceFeedbackStatus.REVIEWED.value

    def archive(self, row) -> None:
        row.status = ServiceFeedbackStatus.ARCHIVED.value
''',
    "ServiceResolution": '''
class ServiceResolutionEngine:
    def submit(self, row) -> None:
        if row.status != ServiceResolutionStatus.DRAFT.value:
            raise InvalidServiceResolutionState("Only draft resolutions can be submitted")
        row.status = ServiceResolutionStatus.SUBMITTED.value

    def complete(self, row) -> None:
        if row.status != ServiceResolutionStatus.SUBMITTED.value:
            raise InvalidServiceResolutionState("Only submitted resolutions can complete")
        row.status = ServiceResolutionStatus.COMPLETED.value

    def cancel(self, row) -> None:
        row.status = ServiceResolutionStatus.CANCELLED.value
''',
    "ServiceDocument": '''
class ServiceDocumentEngine:
    def supersede(self, row) -> None:
        row.status = ServiceDocumentStatus.SUPERSEDED.value

    def archive(self, row) -> None:
        row.status = ServiceDocumentStatus.ARCHIVED.value
''',
    "ServiceNotification": '''
class ServiceNotificationEngine:
    def archive(self, row) -> None:
        row.status = ServiceNotificationStatus.ARCHIVED.value
''',
    "ServiceContract": '''
class ServiceContractEngine:
    def submit(self, row) -> None:
        if row.status != ServiceContractStatus.DRAFT.value:
            raise InvalidServiceContractState("Only draft contracts can be submitted")
        row.status = ServiceContractStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceContractStatus.SUBMITTED.value:
            raise InvalidServiceContractState("Only submitted contracts can be approved")
        row.status = ServiceContractStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != ServiceContractStatus.APPROVED.value:
            raise InvalidServiceContractState("Only approved contracts can activate")
        row.status = ServiceContractStatus.ACTIVE.value

    def expire(self, row) -> None:
        row.status = ServiceContractStatus.EXPIRED.value

    def cancel(self, row) -> None:
        row.status = ServiceContractStatus.CANCELLED.value
''',
    "ServiceReport": '''
class ServiceReportEngine:
    def finalize(self, row) -> None:
        if row.status != ServiceReportStatus.DRAFT.value:
            raise InvalidServiceReportState("Only draft reports can finalize")
        row.status = ServiceReportStatus.FINALIZED.value
''',
}

# flake8: noqa
# This file is exec'd / concatenated into _gen_service_module.py — see assemble script.


def gen_scaffold() -> None:
    w(SVC / "__init__.py", '"""Service Management module — Sprint 16."""\n')
    w(SVC / "domain" / "__init__.py", '"""Service domain layer."""\n')
    w(SVC / "adapters" / "__init__.py", '"""Service cross-module adapters."""\n')
    w(SVC / "service" / "__init__.py", '"""Service services — populated after generation."""\n')
    w(SVC / "service" / "engines" / "__init__.py", '"""Service engines — populated after generation."""\n')
    w(SVC / "repository" / "__init__.py", '"""Service repositories."""\n')
    w(SVC / "models" / "__init__.py", '"""Service models — populated after generation."""\n')
    w(
        SVC / "models" / "mixins.py",
        '''"""Service ORM mixin bundles per ERD_16."""

from database.mixins import (
    AuditMixin,
    BranchMixin,
    CompanyMixin,
    SoftDeleteMixin,
    TenantMixin,
    VersionMixin,
)

SvcMasterMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    SoftDeleteMixin,
    VersionMixin,
)

SvcTransactionMixin = (
    AuditMixin,
    TenantMixin,
    CompanyMixin,
    BranchMixin,
    SoftDeleteMixin,
    VersionMixin,
)

SvcDetailMixin = (
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
        SVC / "domain" / "enums.py",
        '''"""Service domain enums per ERD_16 section 11."""

from enum import Enum


class ServiceCategoryStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ServiceRequestStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ServiceTicketStatus(str, Enum):
    OPEN = "open"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ServiceAssignmentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceScheduleStatus(str, Enum):
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceWorkOrderStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ServiceTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class ServiceChecklistStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceVisitStatus(str, Enum):
    PLANNED = "planned"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceMaterialStatus(str, Enum):
    RESERVED = "reserved"
    ISSUED = "issued"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class ServiceTimeEntryStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    VOID = "void"


class ServiceExpenseStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    POSTED = "posted"
    CANCELLED = "cancelled"


class ServiceSlaStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ServiceEscalationStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class ServiceFeedbackStatus(str, Enum):
    CAPTURED = "captured"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class ServiceResolutionStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceDocumentStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ServiceNotificationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ServiceContractStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ServiceReportStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class SvcEntityType(str, Enum):
    REQUEST = "request"
    TICKET = "ticket"
    ASSIGNMENT = "assignment"
    SCHEDULE = "schedule"
    WORK_ORDER = "work_order"
    VISIT = "visit"
    EXPENSE = "expense"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    CONTRACT = "contract"
    REPORT = "report"
    CATEGORY = "category"
    SLA = "sla"


CODE_PREFIXES: dict[SvcEntityType, tuple[str, int, bool]] = {
    SvcEntityType.REQUEST: ("SR-", 6, True),
    SvcEntityType.TICKET: ("TKT-", 6, True),
    SvcEntityType.ASSIGNMENT: ("SASN-", 6, True),
    SvcEntityType.SCHEDULE: ("SSCH-", 6, True),
    SvcEntityType.WORK_ORDER: ("WO-SRV-", 6, True),
    SvcEntityType.VISIT: ("SVIS-", 6, True),
    SvcEntityType.EXPENSE: ("SEXP-", 6, True),
    SvcEntityType.ESCALATION: ("SESC-", 6, True),
    SvcEntityType.RESOLUTION: ("SRES-", 6, True),
    SvcEntityType.CONTRACT: ("SC-", 6, True),
    SvcEntityType.REPORT: ("SRPT-", 6, True),
    SvcEntityType.CATEGORY: ("SCAT-", 6, False),
    SvcEntityType.SLA: ("SSLA-", 6, False),
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
        SVC / "domain" / "exceptions.py",
        '"""Service domain exceptions."""\n\nfrom core.exceptions import ConflictException\n'
        + "".join(exc_lines),
    )
    w(
        SVC / "domain" / "value_objects.py",
        '''"""Service value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ServiceAmount:
    amount: Decimal
    currency_code: str


@dataclass(frozen=True)
class ServiceCodes:
    document_number: str
''',
    )
    w(
        SVC / "domain" / "entities.py",
        '''"""Service domain entity markers."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class ServiceRequestIdentity:
    request_id: UUID
    document_number: str
    customer_id: UUID
''',
    )


def gen_models() -> None:
    for key, body in MODELS.items():
        w(SVC / "models" / f"{key}.py", body)
    imports = "\n".join(f"from modules.service.models.{k} import {CLASS_MAP[k]}" for k in CLASS_MAP)
    all_names = ",\n    ".join(f'"{CLASS_MAP[k]}"' for k in CLASS_MAP)
    w(
        SVC / "models" / "__init__.py",
        f'"""Service ORM models."""\n\n{imports}\n\n__all__ = [\n    {all_names},\n]\n',
    )


def gen_migrations() -> None:
    w(
        ALEMBIC / "0267_create_service_schema.py",
        '''"""Create service schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0267_create_service_schema"
down_revision: str | None = "0266_seed_asset_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS service")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS service CASCADE")
''',
    )
    for rev, target, down in MIGRATIONS:
        if target == "schema" or (isinstance(target, str) and target.startswith("seed")):
            continue
        if isinstance(target, list):
            imports = "\n".join(
                f"from modules.service.models.{m} import {CLASS_MAP[m]}  # noqa: F401"
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
                f'''"""Create service time entry and expense tables."""

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

from modules.service.models.{target} import {cls}  # noqa: F401

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
    return f'''"""Service {cls} repository."""

from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.service.models import {cls}
from modules.service.repository.base import SvcScopedRepository, utcnow


class {name}Repository(SvcScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get(self, ctx: TenantContext, row_id: UUID) -> {cls} | None:
        stmt = select({cls}).where({cls}.id == row_id, {cls}.is_deleted.is_(False))
        stmt = self.apply_svc_filter(stmt, {cls}, ctx, branch_scoped={branch})
        return self.db.scalar(stmt)

    def list_rows(self, ctx: TenantContext, company_id: UUID):
        stmt = select({cls}).where(
            {cls}.company_id == company_id,
            {cls}.is_deleted.is_(False),
        )
        stmt = self.apply_svc_filter(stmt, {cls}, ctx, branch_scoped={branch})
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
        SVC / "repository" / "base.py",
        '''"""Service scoped repository base."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.base import OrgScopedRepository


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SvcScopedRepository(OrgScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    @staticmethod
    def apply_svc_filter(stmt, model, ctx: TenantContext, *, branch_scoped: bool = False):
        stmt = SvcScopedRepository.apply_tenant_filter(stmt, model, ctx)
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
            SvcScopedRepository.ensure_company_access(ctx, company_id)
            return company_id
        if ctx.company_id is None:
            raise ForbiddenException("Company context required")
        return ctx.company_id
''',
    )
    w(
        SVC / "repository" / "code_sequence_repository.py",
        '''"""Service document code sequences."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.service.domain.enums import CODE_PREFIXES, SvcEntityType


class CodeSequenceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def next_code(self, entity: SvcEntityType, company_id: UUID, model, code_column: str) -> str:
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
        w(SVC / "repository" / f"{module}_repository.py", repo_template(module, cls, name, branch))


def gen_engines() -> None:
    for eng_name, body in ENGINE_BODIES.items():
        fname = ENGINE_FILE_MAP[eng_name]
        w(
            SVC / "service" / "engines" / f"{fname}_engine.py",
            f'"""{eng_name} lifecycle engine."""\n{ENGINE_IMPORTS}\n{body}\n',
        )
    lines = [
        f"from modules.service.service.engines.{ENGINE_FILE_MAP[n]}_engine import {n}Engine"
        for n in ENGINE_BODIES
    ]
    all_names = ",\n    ".join(f'"{n}Engine"' for n in ENGINE_BODIES)
    w(
        SVC / "service" / "engines" / "__init__.py",
        '"""Service business engines."""\n\n'
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
from modules.service.models import {cls}
from modules.service.repository.{entity}_repository import {repo_name}Repository
from modules.service.service.engines import {eng}Engine
from modules.service.service.service_scope_validator import ServiceScopeValidator


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = ServiceScopeValidator(db)
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
            entity_name="svc_{entity}",
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
    if branch_required:
        create_body = f'''
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(SvcEntityType.{entity_type}, cid, {cls}, "{code_col}")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, {code_col}=doc, **fields)
'''
        create_sig = "self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields"
    else:
        create_body = f'''
        cid = self._scope.resolve_company_id(ctx, company_id)
        doc = self._numbers.generate(SvcEntityType.{entity_type}, cid, {cls}, "{code_col}")
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
from modules.service.domain.enums import SvcEntityType
from modules.service.models import {cls}
from modules.service.repository.{entity}_repository import {repo_name}Repository
from modules.service.service.document_number_service import DocumentNumberService
from modules.service.service.engines import {engine_name}Engine
from modules.service.service.service_scope_validator import ServiceScopeValidator


class {svc_name}:
    def __init__(self, db: Session) -> None:
        self._repo = {repo_name}Repository(db)
        self._scope = ServiceScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = {engine_name}Engine()
        self._audit = AuditService(db)

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
        SVC / "service" / "service_scope_validator.py",
        '''"""Service scope validator."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.service.repository.base import SvcScopedRepository


class ServiceScopeValidator(SvcScopedRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def validate_company_access(self, ctx: TenantContext, company_id: UUID) -> None:
        self.ensure_company_access(ctx, company_id)

    def validate_branch_access(self, ctx: TenantContext, branch_id: UUID) -> None:
        self.ensure_branch_access(ctx, branch_id)
''',
    )
    w(
        SVC / "service" / "document_number_service.py",
        '''"""Service document numbering."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.service.domain.enums import SvcEntityType
from modules.service.repository.code_sequence_repository import CodeSequenceRepository


class DocumentNumberService:
    def __init__(self, db: Session) -> None:
        self._seq = CodeSequenceRepository(db)

    def generate(self, entity: SvcEntityType, company_id: UUID, model, code_column: str) -> str:
        return self._seq.next_code(entity, company_id, model, code_column)
''',
    )

    simple = [
        ("ServiceCategoryService", "SvcServiceCategory", "ServiceCategory", "service_category", False, "ServiceCategory"),
        ("ServiceTicketService", "SvcServiceTicket", "ServiceTicket", "service_ticket", True, "ServiceTicket"),
        ("ServiceTaskService", "SvcServiceTask", "ServiceTask", "service_task", False, "ServiceTask"),
        ("ServiceChecklistService", "SvcServiceChecklist", "ServiceChecklist", "service_checklist", False, "ServiceChecklist"),
        ("ServiceMaterialService", "SvcServiceMaterial", "ServiceMaterial", "service_material", False, "ServiceMaterial"),
        ("ServiceTimeEntryService", "SvcServiceTimeEntry", "ServiceTimeEntry", "service_time_entry", False, "ServiceTimeEntry"),
        ("ServiceSLAService", "SvcServiceSla", "ServiceSla", "service_sla", False, "ServiceSla"),
        ("ServiceFeedbackService", "SvcServiceFeedback", "ServiceFeedback", "service_feedback", False, "ServiceFeedback"),
        ("ServiceDocumentService", "SvcServiceDocument", "ServiceDocument", "service_document", False, "ServiceDocument"),
        ("ServiceNotificationService", "SvcServiceNotification", "ServiceNotification", "service_notification", False, "ServiceNotification"),
    ]
    file_map_simple = {
        "ServiceCategoryService": "service_category_service.py",
        "ServiceTicketService": "service_ticket_service.py",
        "ServiceTaskService": "service_task_service.py",
        "ServiceChecklistService": "service_checklist_service.py",
        "ServiceMaterialService": "service_material_service.py",
        "ServiceTimeEntryService": "service_time_entry_service.py",
        "ServiceSLAService": "service_sla_service.py",
        "ServiceFeedbackService": "service_feedback_service.py",
        "ServiceDocumentService": "service_document_service.py",
        "ServiceNotificationService": "service_notification_service.py",
    }
    for svc, cls, repo, entity, branch, eng in simple:
        w(SVC / "service" / file_map_simple[svc], catalog_service(svc, cls, repo, entity, branch, eng))

    # Override SLA service file name expectation - ServiceSLAService uses ServiceSla engine
    # Ticket is catalog but needs document number - rewrite as numbered
    w(
        SVC / "service" / "service_ticket_service.py",
        numbered_service(
            "ServiceTicketService",
            "SvcServiceTicket",
            "ServiceTicket",
            "service_ticket",
            "TICKET",
            "document_number",
            True,
            "ServiceTicket",
            [],
        ),
    )
    w(
        SVC / "service" / "service_request_service.py",
        numbered_service(
            "ServiceRequestService",
            "SvcServiceRequest",
            "ServiceRequest",
            "service_request",
            "REQUEST",
            "document_number",
            True,
            "ServiceRequest",
            ["submit", "approve"],
        ),
    )
    w(
        SVC / "service" / "service_assignment_service.py",
        numbered_service(
            "ServiceAssignmentService",
            "SvcServiceAssignment",
            "ServiceAssignment",
            "service_assignment",
            "ASSIGNMENT",
            "document_number",
            True,
            "ServiceAssignment",
            ["complete"],
        ),
    )
    w(
        SVC / "service" / "service_schedule_service.py",
        numbered_service(
            "ServiceScheduleService",
            "SvcServiceSchedule",
            "ServiceSchedule",
            "service_schedule",
            "SCHEDULE",
            "document_number",
            True,
            "ServiceSchedule",
            ["complete"],
        ),
    )
    w(
        SVC / "service" / "work_order_service.py",
        numbered_service(
            "WorkOrderService",
            "SvcServiceWorkOrder",
            "ServiceWorkOrder",
            "service_work_order",
            "WORK_ORDER",
            "document_number",
            True,
            "ServiceWorkOrder",
            ["submit", "approve", "complete"],
        ),
    )
    w(
        SVC / "service" / "service_visit_service.py",
        numbered_service(
            "ServiceVisitService",
            "SvcServiceVisit",
            "ServiceVisit",
            "service_visit",
            "VISIT",
            "document_number",
            True,
            "ServiceVisit",
            ["complete"],
        ),
    )
    w(
        SVC / "service" / "service_escalation_service.py",
        numbered_service(
            "ServiceEscalationService",
            "SvcServiceEscalation",
            "ServiceEscalation",
            "service_escalation",
            "ESCALATION",
            "document_number",
            True,
            "ServiceEscalation",
            ["escalate"],
        ),
    )
    w(
        SVC / "service" / "service_resolution_service.py",
        numbered_service(
            "ServiceResolutionService",
            "SvcServiceResolution",
            "ServiceResolution",
            "service_resolution",
            "RESOLUTION",
            "document_number",
            True,
            "ServiceResolution",
            ["submit", "complete"],
        ),
    )
    w(
        SVC / "service" / "service_contract_service.py",
        numbered_service(
            "ServiceContractService",
            "SvcServiceContract",
            "ServiceContract",
            "service_contract",
            "CONTRACT",
            "document_number",
            True,
            "ServiceContract",
            ["submit", "approve"],
        ),
    )
    w(
        SVC / "service" / "service_report_service.py",
        numbered_service(
            "ServiceReportService",
            "SvcServiceReport",
            "ServiceReport",
            "service_report",
            "REPORT",
            "report_code",
            False,
            "ServiceReport",
            ["finalize"],
        ),
    )

    w(
        SVC / "service" / "service_expense_service.py",
        '''"""Service expense service — posts via Finance PostingService only."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.service.adapters.finance_port import ServiceFinanceAdapter
from modules.service.domain.enums import SvcEntityType
from modules.service.models import SvcServiceExpense
from modules.service.repository.service_expense_repository import ServiceExpenseRepository
from modules.service.service.document_number_service import DocumentNumberService
from modules.service.service.engines import ServiceExpenseEngine
from modules.service.service.service_scope_validator import ServiceScopeValidator


class ServiceExpenseService:
    def __init__(self, db: Session) -> None:
        self._repo = ServiceExpenseRepository(db)
        self._scope = ServiceScopeValidator(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ServiceExpenseEngine()
        self._finance = ServiceFinanceAdapter(db)
        self._audit = AuditService(db)

    def list(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_rows(ctx, cid)

    def get(self, ctx: TenantContext, row_id: UUID) -> SvcServiceExpense:
        row = self._repo.get(ctx, row_id)
        if row is None:
            raise NotFoundException("ServiceExpenseService not found")
        return row

    def create(self, ctx: TenantContext, *, branch_id: UUID, company_id: UUID | None = None, **fields):
        cid = self._scope.resolve_company_id(ctx, company_id)
        self._scope.validate_branch_access(ctx, branch_id)
        doc = self._numbers.generate(SvcEntityType.EXPENSE, cid, SvcServiceExpense, "document_number")
        return self._repo.create(ctx, company_id=cid, branch_id=branch_id, document_number=doc, **fields)

    def update(self, ctx: TenantContext, row_id: UUID, **fields):
        self.get(ctx, row_id)
        row = self._repo.update(ctx, row_id, **fields)
        if row is None:
            raise NotFoundException("ServiceExpenseService not found")
        return row

    def submit(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.submit(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def approve(self, ctx: TenantContext, row_id: UUID):
        row = self.get(ctx, row_id)
        self._engine.approve(row)
        return self._repo.update(ctx, row_id, status=row.status)

    def post(
        self,
        ctx: TenantContext,
        row_id: UUID,
        *,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ):
        row = self.get(ctx, row_id)
        journal_id = self._finance.post_expense(
            ctx,
            row,
            amount=Decimal(str(row.amount)),
            debit_account_id=debit_account_id,
            credit_account_id=credit_account_id,
            fiscal_year_id=fiscal_year_id,
        )
        self._engine.post(row)
        updated = self._repo.update(
            ctx,
            row_id,
            status=row.status,
            finance_journal_id=journal_id,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="svc_service_expense",
            entity_id=row_id,
            operation="post",
            performed_by=ctx.user_id,
            new_value={"finance_journal_id": str(journal_id), "status": row.status},
        )
        return updated
''',
    )

    w(
        SVC / "service" / "integration_service.py",
        '''"""Service integration — cross-module reads only; no peer ORM writes."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.service.adapters.asset_port import ServiceAssetAdapter
from modules.service.adapters.master_data_port import ServiceMasterDataAdapter
from modules.service.adapters.organization_port import ServiceOrganizationAdapter
from modules.service.adapters.payroll_port import ServicePayrollAdapter


class ServiceIntegrationService:
    def __init__(self, db: Session) -> None:
        self._master = ServiceMasterDataAdapter(db)
        self._org = ServiceOrganizationAdapter(db)
        self._payroll = ServicePayrollAdapter(db)
        self._asset = ServiceAssetAdapter(db)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._master.get_customer(ctx, customer_id)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._master.get_employee(ctx, employee_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._master.get_product(ctx, product_id)

    def get_master_asset(self, ctx: TenantContext, master_asset_id: UUID):
        return self._master.get_asset(ctx, master_asset_id)

    def get_department(self, ctx: TenantContext, department_id: UUID):
        return self._org.get_department(ctx, department_id)

    def labor_cost_hint(self, ctx: TenantContext, employee_id: UUID):
        return self._payroll.labor_cost_hint(ctx, employee_id)

    def resolve_operational_asset(self, asset_id: UUID | None):
        return self._asset.resolve_asset_uuid(asset_id)
''',
    )

    w(
        SVC / "service" / "application_service.py",
        '''"""Service application service facade."""

from sqlalchemy.orm import Session

from modules.service.service.integration_service import ServiceIntegrationService
from modules.service.service.service_assignment_service import ServiceAssignmentService
from modules.service.service.service_category_service import ServiceCategoryService
from modules.service.service.service_checklist_service import ServiceChecklistService
from modules.service.service.service_contract_service import ServiceContractService
from modules.service.service.service_document_service import ServiceDocumentService
from modules.service.service.service_escalation_service import ServiceEscalationService
from modules.service.service.service_expense_service import ServiceExpenseService
from modules.service.service.service_feedback_service import ServiceFeedbackService
from modules.service.service.service_material_service import ServiceMaterialService
from modules.service.service.service_notification_service import ServiceNotificationService
from modules.service.service.service_report_service import ServiceReportService
from modules.service.service.service_request_service import ServiceRequestService
from modules.service.service.service_resolution_service import ServiceResolutionService
from modules.service.service.service_schedule_service import ServiceScheduleService
from modules.service.service.service_sla_service import ServiceSLAService
from modules.service.service.service_task_service import ServiceTaskService
from modules.service.service.service_ticket_service import ServiceTicketService
from modules.service.service.service_time_entry_service import ServiceTimeEntryService
from modules.service.service.service_visit_service import ServiceVisitService
from modules.service.service.work_order_service import WorkOrderService


class ServiceApplicationService:
    def __init__(self, db: Session) -> None:
        self.categories = ServiceCategoryService(db)
        self.requests = ServiceRequestService(db)
        self.tickets = ServiceTicketService(db)
        self.assignments = ServiceAssignmentService(db)
        self.schedules = ServiceScheduleService(db)
        self.work_orders = WorkOrderService(db)
        self.tasks = ServiceTaskService(db)
        self.checklists = ServiceChecklistService(db)
        self.visits = ServiceVisitService(db)
        self.materials = ServiceMaterialService(db)
        self.time_entries = ServiceTimeEntryService(db)
        self.expenses = ServiceExpenseService(db)
        self.slas = ServiceSLAService(db)
        self.escalations = ServiceEscalationService(db)
        self.feedback = ServiceFeedbackService(db)
        self.resolutions = ServiceResolutionService(db)
        self.documents = ServiceDocumentService(db)
        self.notifications = ServiceNotificationService(db)
        self.contracts = ServiceContractService(db)
        self.reports = ServiceReportService(db)
        self.integration = ServiceIntegrationService(db)
''',
    )

    svc_exports = [
        "ServiceApplicationService",
        "ServiceAssignmentService",
        "ServiceCategoryService",
        "ServiceChecklistService",
        "ServiceContractService",
        "ServiceDocumentService",
        "ServiceEscalationService",
        "ServiceExpenseService",
        "ServiceFeedbackService",
        "ServiceIntegrationService",
        "ServiceMaterialService",
        "ServiceNotificationService",
        "ServiceReportService",
        "ServiceRequestService",
        "ServiceResolutionService",
        "ServiceSLAService",
        "ServiceScheduleService",
        "ServiceTaskService",
        "ServiceTicketService",
        "ServiceTimeEntryService",
        "ServiceVisitService",
        "WorkOrderService",
    ]
    import_lines = [
        "from modules.service.service.application_service import ServiceApplicationService",
        "from modules.service.service.integration_service import ServiceIntegrationService",
        "from modules.service.service.service_assignment_service import ServiceAssignmentService",
        "from modules.service.service.service_category_service import ServiceCategoryService",
        "from modules.service.service.service_checklist_service import ServiceChecklistService",
        "from modules.service.service.service_contract_service import ServiceContractService",
        "from modules.service.service.service_document_service import ServiceDocumentService",
        "from modules.service.service.service_escalation_service import ServiceEscalationService",
        "from modules.service.service.service_expense_service import ServiceExpenseService",
        "from modules.service.service.service_feedback_service import ServiceFeedbackService",
        "from modules.service.service.service_material_service import ServiceMaterialService",
        "from modules.service.service.service_notification_service import ServiceNotificationService",
        "from modules.service.service.service_report_service import ServiceReportService",
        "from modules.service.service.service_request_service import ServiceRequestService",
        "from modules.service.service.service_resolution_service import ServiceResolutionService",
        "from modules.service.service.service_schedule_service import ServiceScheduleService",
        "from modules.service.service.service_sla_service import ServiceSLAService",
        "from modules.service.service.service_task_service import ServiceTaskService",
        "from modules.service.service.service_ticket_service import ServiceTicketService",
        "from modules.service.service.service_time_entry_service import ServiceTimeEntryService",
        "from modules.service.service.service_visit_service import ServiceVisitService",
        "from modules.service.service.work_order_service import WorkOrderService",
    ]
    all_names = ",\n    ".join(f'"{n}"' for n in svc_exports)
    w(
        SVC / "service" / "__init__.py",
        '"""Service Management services."""\n\n'
        + "\n".join(import_lines)
        + f"\n\n__all__ = [\n    {all_names},\n]\n",
    )


def gen_adapters() -> None:
    w(
        SVC / "adapters" / "master_data_port.py",
        '''"""Master Data port — customer / employee / asset / product (C-01)."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.service.asset_service import AssetService as MasterAssetService
from modules.master_data.service.customer_service import CustomerService
from modules.master_data.service.employee_service import EmployeeService
from modules.master_data.service.product_service import ProductService


class ServiceMasterDataAdapter:
    def __init__(self, db: Session) -> None:
        self._customers = CustomerService(db)
        self._employees = EmployeeService(db)
        self._assets = MasterAssetService(db)
        self._products = ProductService(db)

    def get_customer(self, ctx: TenantContext, customer_id: UUID):
        return self._customers.get_customer(ctx, customer_id)

    def get_employee(self, ctx: TenantContext, employee_id: UUID):
        return self._employees.get_employee(ctx, employee_id)

    def get_asset(self, ctx: TenantContext, master_asset_id: UUID):
        return self._assets.get_asset(ctx, master_asset_id)

    def get_product(self, ctx: TenantContext, product_id: UUID):
        return self._products.get_product(ctx, product_id)
''',
    )
    w(
        SVC / "adapters" / "organization_port.py",
        '''"""Organization port — read org_department only."""

from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.organization.repository.hierarchy_repository import DepartmentRepository


class ServiceOrganizationAdapter:
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
        SVC / "adapters" / "finance_port.py",
        '''"""Finance port — JournalService + PostingService.post_system_journal only."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.finance.domain.enums import JournalType
from modules.finance.service.journal_service import JournalService
from modules.finance.service.posting_service import PostingService
from modules.foundation.domain.value_objects import TenantContext
from modules.service.models import SvcServiceExpense


class ServiceFinanceAdapter:
    def __init__(self, db: Session) -> None:
        self._journals = JournalService(db)
        self._posting = PostingService(db)

    def post_expense(
        self,
        ctx: TenantContext,
        row: SvcServiceExpense,
        *,
        amount: Decimal,
        debit_account_id: UUID,
        credit_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> UUID:
        amount = amount.quantize(Decimal("0.0001"))
        journal = self._journals.create_journal(
            ctx,
            company_id=row.company_id,
            branch_id=row.branch_id,
            journal_date=row.incurred_on or date.today(),
            description=f"Service expense {row.document_number}",
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
            description="Service expense debit",
        )
        self._journals.add_line(
            ctx,
            journal.id,
            line_number=2,
            account_id=credit_account_id,
            debit_amount=0,
            credit_amount=float(amount),
            description="Service expense credit",
        )
        self._posting.post_system_journal(ctx, journal.id)
        return journal.id
''',
    )
    w(
        SVC / "adapters" / "asset_port.py",
        '''"""Asset port — UUID-only stubs; no ast_* FK or ORM writes."""

from uuid import UUID


class ServiceAssetAdapter:
    def __init__(self, db=None) -> None:
        self._db = db

    def resolve_asset_uuid(self, asset_id: UUID | None) -> dict:
        return {"asset_id": asset_id, "linked": asset_id is not None}

    def resolve_maintenance_plan_uuid(self, maintenance_plan_id: UUID | None) -> dict:
        return {"maintenance_plan_id": maintenance_plan_id, "linked": maintenance_plan_id is not None}
''',
    )
    w(
        SVC / "adapters" / "payroll_port.py",
        '''"""Payroll port — optional read-only labor cost hint; no pay_* writes."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.payroll.repository.employee_salary_repository import EmployeeSalaryRepository


class ServicePayrollAdapter:
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
        SVC / "adapters" / "__init__.py",
        '''"""Service adapters."""

from modules.service.adapters.asset_port import ServiceAssetAdapter
from modules.service.adapters.finance_port import ServiceFinanceAdapter
from modules.service.adapters.master_data_port import ServiceMasterDataAdapter
from modules.service.adapters.organization_port import ServiceOrganizationAdapter
from modules.service.adapters.payroll_port import ServicePayrollAdapter

__all__ = [
    "ServiceAssetAdapter",
    "ServiceFinanceAdapter",
    "ServiceMasterDataAdapter",
    "ServiceOrganizationAdapter",
    "ServicePayrollAdapter",
]
''',
    )


def gen_permissions() -> None:
    w(
        SVC / "permissions.py",
        '''"""Service permission constants per ERD_16 section 14."""

SERVICE_PERMISSIONS: list[tuple[str, str, str, str]] = [
    ("service.category:read", "service.category", "read", "service"),
    ("service.category:create", "service.category", "create", "service"),
    ("service.category:update", "service.category", "update", "service"),
    ("service.request:read", "service.request", "read", "service"),
    ("service.request:create", "service.request", "create", "service"),
    ("service.request:update", "service.request", "update", "service"),
    ("service.request:submit", "service.request", "submit", "service"),
    ("service.request:approve", "service.request", "approve", "service"),
    ("service.ticket:read", "service.ticket", "read", "service"),
    ("service.ticket:create", "service.ticket", "create", "service"),
    ("service.ticket:update", "service.ticket", "update", "service"),
    ("service.assignment:read", "service.assignment", "read", "service"),
    ("service.assignment:create", "service.assignment", "create", "service"),
    ("service.assignment:update", "service.assignment", "update", "service"),
    ("service.assignment:complete", "service.assignment", "complete", "service"),
    ("service.schedule:read", "service.schedule", "read", "service"),
    ("service.schedule:create", "service.schedule", "create", "service"),
    ("service.schedule:update", "service.schedule", "update", "service"),
    ("service.schedule:complete", "service.schedule", "complete", "service"),
    ("service.work_order:read", "service.work_order", "read", "service"),
    ("service.work_order:create", "service.work_order", "create", "service"),
    ("service.work_order:submit", "service.work_order", "submit", "service"),
    ("service.work_order:approve", "service.work_order", "approve", "service"),
    ("service.work_order:complete", "service.work_order", "complete", "service"),
    ("service.task:read", "service.task", "read", "service"),
    ("service.task:create", "service.task", "create", "service"),
    ("service.task:update", "service.task", "update", "service"),
    ("service.task:complete", "service.task", "complete", "service"),
    ("service.checklist:read", "service.checklist", "read", "service"),
    ("service.checklist:create", "service.checklist", "create", "service"),
    ("service.checklist:update", "service.checklist", "update", "service"),
    ("service.checklist:complete", "service.checklist", "complete", "service"),
    ("service.visit:read", "service.visit", "read", "service"),
    ("service.visit:create", "service.visit", "create", "service"),
    ("service.visit:update", "service.visit", "update", "service"),
    ("service.visit:complete", "service.visit", "complete", "service"),
    ("service.material:read", "service.material", "read", "service"),
    ("service.material:create", "service.material", "create", "service"),
    ("service.material:update", "service.material", "update", "service"),
    ("service.time_entry:read", "service.time_entry", "read", "service"),
    ("service.time_entry:create", "service.time_entry", "create", "service"),
    ("service.time_entry:update", "service.time_entry", "update", "service"),
    ("service.expense:read", "service.expense", "read", "service"),
    ("service.expense:create", "service.expense", "create", "service"),
    ("service.expense:submit", "service.expense", "submit", "service"),
    ("service.expense:approve", "service.expense", "approve", "service"),
    ("service.expense:post", "service.expense", "post", "service"),
    ("service.sla:read", "service.sla", "read", "service"),
    ("service.sla:create", "service.sla", "create", "service"),
    ("service.sla:update", "service.sla", "update", "service"),
    ("service.escalation:read", "service.escalation", "read", "service"),
    ("service.escalation:create", "service.escalation", "create", "service"),
    ("service.escalation:update", "service.escalation", "update", "service"),
    ("service.escalation:escalate", "service.escalation", "escalate", "service"),
    ("service.feedback:read", "service.feedback", "read", "service"),
    ("service.feedback:create", "service.feedback", "create", "service"),
    ("service.feedback:complete", "service.feedback", "complete", "service"),
    ("service.resolution:read", "service.resolution", "read", "service"),
    ("service.resolution:create", "service.resolution", "create", "service"),
    ("service.resolution:complete", "service.resolution", "complete", "service"),
    ("service.contract:read", "service.contract", "read", "service"),
    ("service.contract:create", "service.contract", "create", "service"),
    ("service.contract:submit", "service.contract", "submit", "service"),
    ("service.contract:approve", "service.contract", "approve", "service"),
    ("service.document:read", "service.document", "read", "service"),
    ("service.document:create", "service.document", "create", "service"),
    ("service.document:update", "service.document", "update", "service"),
    ("service.notification:read", "service.notification", "read", "service"),
    ("service.notification:create", "service.notification", "create", "service"),
    ("service.notification:update", "service.notification", "update", "service"),
    ("service.report:read", "service.report", "read", "service"),
    ("service.report:export", "service.report", "export", "service"),
]

_ALL = [p[0] for p in SERVICE_PERMISSIONS]

SERVICE_MANAGER_PERMISSIONS = list(_ALL)
SERVICE_ENGINEER_PERMISSIONS = [
    p for p in _ALL
    if not any(
        x in p
        for x in (
            ":approve",
            "expense:post",
            "contract:submit",
            "contract:approve",
            "category:create",
            "category:update",
            "sla:create",
            "sla:update",
            "report:export",
        )
    )
]
SERVICE_COORDINATOR_PERMISSIONS = [
    p for p in _ALL
    if not any(
        x in p
        for x in (
            "expense:post",
            "contract:approve",
            "category:create",
            "category:update",
            "sla:create",
            "sla:update",
        )
    )
]
SERVICE_ADMIN_PERMISSIONS = list(_ALL)
''',
    )

def gen_api() -> None:
    w(
        SVC / "dependencies.py",
        '''"""Service module dependencies."""

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
        '"""Service Pydantic schemas."""',
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
        "class FinancePostRequest(BaseModel):",
        "    debit_account_id: UUID",
        "    credit_account_id: UUID",
        "    fiscal_year_id: UUID | None = None",
    ]
    w(SVC / "schemas.py", "\n".join(schema_lines) + "\n")

    router_parts: list[str] = [
        '"""Service API route handlers."""',
        "",
        "from typing import Annotated",
        "from uuid import UUID",
        "",
        "from fastapi import APIRouter, Depends",
        "from sqlalchemy.orm import Session",
        "",
        "from modules.service.dependencies import (",
        "    PaginationParams,",
        "    extract_update_fields,",
        "    get_db,",
        "    get_pagination,",
        "    paginate,",
        "    require_permission,",
        ")",
        "from modules.service.schemas import (",
    ]
    for _, name, _, _, _ in ROUTE_SPECS:
        router_parts.append(f"    {name}Create,")
        router_parts.append(f"    {name}Response,")
        router_parts.append(f"    {name}Update,")
    router_parts += [
        "    FinancePostRequest,",
        ")",
        "from modules.service.service import (",
    ]
    for _, _, svc, _, _ in ROUTE_SPECS:
        router_parts.append(f"    {svc},")
    router_parts.append(")")
    router_parts.append("from modules.foundation.domain.value_objects import TenantContext")
    router_parts.append("from shared.schemas import APIResponse")
    router_parts.append("")

    exports: list[str] = []
    for prefix, name, svc, perm, branch in ROUTE_SPECS:
        rname = f"{prefix.replace('-', '_')}_router"
        exports.append(rname)
        router_parts.append(f'{rname} = APIRouter(prefix="/{prefix}", tags=["Service — {name}"])')
        router_parts.append("")
        if branch:
            create_call = (
                f"{svc}(db).create(ctx, branch_id=body.branch_id, "
                f"**body.model_dump(exclude={{'branch_id'}}, exclude_none=True))"
            )
        else:
            create_call = f"{svc}(db).create(ctx, **body.model_dump(exclude_none=True))"

        update_perm = f"{perm}:export" if perm == "service.report" else f"{perm}:update"
        if perm == "service.work_order":
            update_perm = "service.work_order:create"
        elif perm == "service.expense":
            update_perm = "service.expense:create"
        elif perm == "service.contract":
            update_perm = "service.contract:create"
        elif perm == "service.resolution":
            update_perm = "service.resolution:create"
        elif perm == "service.feedback":
            update_perm = "service.feedback:create"

        create_perm = f"{perm}:create"
        if perm == "service.report":
            create_perm = "service.report:export"

        fn = prefix.replace("-", "_")
        router_parts += [
            f'@{rname}.get("", response_model=APIResponse[list[{name}Response]])',
            f"def list_{fn}(",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:read"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "    pagination: Annotated[PaginationParams, Depends(get_pagination)],",
            "    company_id: UUID | None = None,",
            "):",
            f"    items = {svc}(db).list(ctx, company_id=company_id)",
            '    return APIResponse(message="OK", data=paginate(items, pagination))',
            "",
            f'@{rname}.get("/{{row_id}}", response_model=APIResponse[{name}Response])',
            f"def get_{fn}(",
            "    row_id: UUID,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{perm}:read"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="OK", data={svc}(db).get(ctx, row_id))',
            "",
            f'@{rname}.post("", response_model=APIResponse[{name}Response])',
            f"def create_{fn}(",
            f"    body: {name}Create,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{create_perm}"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="Created", data={create_call})',
            "",
            f'@{rname}.patch("/{{row_id}}", response_model=APIResponse[{name}Response])',
            f"def update_{fn}(",
            "    row_id: UUID,",
            f"    body: {name}Update,",
            f'    ctx: Annotated[TenantContext, Depends(require_permission("{update_perm}"))],',
            "    db: Annotated[Session, Depends(get_db)],",
            "):",
            f'    return APIResponse(message="Updated", data={svc}(db).update(ctx, row_id, **extract_update_fields(body)))',
            "",
        ]

        actions: list[tuple[str, str]] = []
        if svc == "ServiceRequestService":
            actions = [("submit", "service.request:submit"), ("approve", "service.request:approve")]
        elif svc == "WorkOrderService":
            actions = [
                ("submit", "service.work_order:submit"),
                ("approve", "service.work_order:approve"),
                ("complete", "service.work_order:complete"),
            ]
        elif svc == "ServiceExpenseService":
            actions = [
                ("submit", "service.expense:submit"),
                ("approve", "service.expense:approve"),
            ]
        elif svc == "ServiceEscalationService":
            actions = [("escalate", "service.escalation:escalate")]
        elif svc == "ServiceResolutionService":
            actions = [
                ("submit", "service.resolution:create"),
                ("complete", "service.resolution:complete"),
            ]
        elif svc == "ServiceContractService":
            actions = [
                ("submit", "service.contract:submit"),
                ("approve", "service.contract:approve"),
            ]
        elif svc == "ServiceAssignmentService":
            actions = [("complete", "service.assignment:complete")]
        elif svc == "ServiceScheduleService":
            actions = [("complete", "service.schedule:complete")]
        elif svc == "ServiceVisitService":
            actions = [("complete", "service.visit:complete")]

        for act, pcode in actions:
            router_parts += [
                f'@{rname}.post("/{{row_id}}/{act}", response_model=APIResponse[{name}Response])',
                f"def {act}_{fn}(",
                "    row_id: UUID,",
                f'    ctx: Annotated[TenantContext, Depends(require_permission("{pcode}"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f'    return APIResponse(message="{act}", data={svc}(db).{act}(ctx, row_id))',
                "",
            ]

        if svc == "ServiceExpenseService":
            router_parts += [
                f'@{rname}.post("/{{row_id}}/post", response_model=APIResponse[{name}Response])',
                f"def post_{fn}(",
                "    row_id: UUID,",
                "    body: FinancePostRequest,",
                '    ctx: Annotated[TenantContext, Depends(require_permission("service.expense:post"))],',
                "    db: Annotated[Session, Depends(get_db)],",
                "):",
                f"    data = {svc}(db).post(",
                "        ctx,",
                "        row_id,",
                "        debit_account_id=body.debit_account_id,",
                "        credit_account_id=body.credit_account_id,",
                "        fiscal_year_id=body.fiscal_year_id,",
                "    )",
                '    return APIResponse(message="Posted", data=data)',
                "",
            ]

    w(SVC / "routers" / "__init__.py", "\n".join(router_parts) + "\n")

    import_list = ",\n    ".join(exports)
    w(
        SVC / "router.py",
        f'''"""Service module router aggregation."""

from fastapi import APIRouter

from modules.service.routers import (
    {import_list},
)

service_router = APIRouter(prefix="/service")
'''
        + "\n".join(f"service_router.include_router({e})" for e in exports)
        + "\n",
    )


def gen_tasks_tests() -> None:
    w(
        SVC / "tasks.py",
        '''"""Service Celery task stubs per ERD_16 section 15."""

from workers.celery_app import celery_app


@celery_app.task(name="service.sla_breach_monitor")
def sla_breach_monitor() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceRequest

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceRequest).where(
                    SvcServiceRequest.is_deleted.is_(False),
                    SvcServiceRequest.sla_status.in_(["at_risk", "breached"]),
                )
            ).all()
        )
        return {"status": "ok", "at_risk_or_breached": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.work_order_reminders")
def work_order_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceWorkOrder

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceWorkOrder).where(
                    SvcServiceWorkOrder.is_deleted.is_(False),
                    SvcServiceWorkOrder.status.in_(["approved", "assigned", "in_progress"]),
                )
            ).all()
        )
        return {"status": "ok", "open_work_orders": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.preventive_service_scheduler")
def preventive_service_scheduler() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceContract

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceContract).where(
                    SvcServiceContract.is_deleted.is_(False),
                    SvcServiceContract.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "active_contracts": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.service_contract_expiry")
def service_contract_expiry() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceContract

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceContract).where(
                    SvcServiceContract.is_deleted.is_(False),
                    SvcServiceContract.status == "active",
                )
            ).all()
        )
        return {"status": "ok", "contracts_to_review": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.customer_feedback_reminders")
def customer_feedback_reminders() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceResolution

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceResolution).where(
                    SvcServiceResolution.is_deleted.is_(False),
                    SvcServiceResolution.status == "completed",
                )
            ).all()
        )
        return {"status": "ok", "completed_resolutions": len(rows)}
    finally:
        db.close()


@celery_app.task(name="service.retry_finance_posting")
def retry_finance_posting() -> dict:
    from sqlalchemy import select

    from database.session import SessionLocal
    from modules.service.models import SvcServiceExpense

    db = SessionLocal()
    try:
        rows = list(
            db.scalars(
                select(SvcServiceExpense).where(
                    SvcServiceExpense.is_deleted.is_(False),
                    SvcServiceExpense.status == "approved",
                    SvcServiceExpense.finance_journal_id.is_(None),
                )
            ).all()
        )
        return {"status": "ok", "unposted_expenses": len(rows)}
    finally:
        db.close()
''',
    )

    w(
        TESTS / "unit" / "service" / "test_service_engines.py",
        '''"""Unit tests for service engines."""

from types import SimpleNamespace

from modules.service.service.engines import (
    ServiceExpenseEngine,
    ServiceRequestEngine,
    ServiceResolutionEngine,
    ServiceWorkOrderEngine,
)


def test_service_request_lifecycle():
    engine = ServiceRequestEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"


def test_work_order_complete():
    engine = ServiceWorkOrderEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.assign(row)
    engine.start(row)
    engine.complete(row)
    assert row.status == "completed"


def test_expense_post():
    engine = ServiceExpenseEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.post(row)
    assert row.status == "posted"


def test_resolution_complete():
    engine = ServiceResolutionEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.complete(row)
    assert row.status == "completed"
''',
    )

    w(
        TESTS / "unit" / "service" / "test_service_tasks.py",
        '''"""Unit tests for service Celery tasks."""

from modules.service import tasks as service_tasks


def test_service_task_names_registered():
    assert service_tasks.sla_breach_monitor.name == "service.sla_breach_monitor"
    assert service_tasks.work_order_reminders.name == "service.work_order_reminders"
    assert service_tasks.preventive_service_scheduler.name == "service.preventive_service_scheduler"
    assert service_tasks.service_contract_expiry.name == "service.service_contract_expiry"
    assert service_tasks.customer_feedback_reminders.name == "service.customer_feedback_reminders"
    assert service_tasks.retry_finance_posting.name == "service.retry_finance_posting"
''',
    )

    w(
        TESTS / "security" / "service" / "test_service_permissions.py",
        '''"""Service RBAC permission tests."""

from modules.service.permissions import (
    SERVICE_ADMIN_PERMISSIONS,
    SERVICE_COORDINATOR_PERMISSIONS,
    SERVICE_ENGINEER_PERMISSIONS,
    SERVICE_MANAGER_PERMISSIONS,
    SERVICE_PERMISSIONS,
)


def test_service_permissions_defined():
    assert len(SERVICE_PERMISSIONS) >= 40
    assert "service.request:approve" in [p[0] for p in SERVICE_PERMISSIONS]
    assert "service.expense:post" in [p[0] for p in SERVICE_PERMISSIONS]


def test_service_roles():
    assert SERVICE_MANAGER_PERMISSIONS
    assert SERVICE_ENGINEER_PERMISSIONS
    assert SERVICE_COORDINATOR_PERMISSIONS
    assert SERVICE_ADMIN_PERMISSIONS
    assert "service.request:approve" in SERVICE_MANAGER_PERMISSIONS
    assert "service.expense:post" in SERVICE_ADMIN_PERMISSIONS
''',
    )

    w(
        TESTS / "integration" / "service" / "test_service_module_import.py",
        '''"""Integration smoke: Service module imports and router mount."""

from modules.service.models import SvcServiceCategory, SvcServiceExpense, SvcServiceRequest
from modules.service.router import service_router
from modules.service.service import (
    ServiceApplicationService,
    ServiceExpenseService,
    ServiceRequestService,
    WorkOrderService,
)
from modules.service.service.engines import ServiceExpenseEngine, ServiceRequestEngine


def test_service_models_importable():
    assert SvcServiceCategory.__tablename__ == "svc_service_category"
    assert SvcServiceRequest.__tablename__ == "svc_service_request"
    assert SvcServiceExpense.__tablename__ == "svc_service_expense"


def test_service_router_mounted():
    assert service_router.prefix == "/service"
    paths = [getattr(r, "path", "") for r in service_router.routes]
    assert any("/{row_id}" in p for p in paths)
    assert any("service-requests" in p for p in paths)
    assert any("work-orders" in p for p in paths)


def test_service_services_and_engines_importable():
    assert ServiceApplicationService
    assert ServiceRequestService
    assert WorkOrderService
    assert ServiceExpenseService
    assert ServiceRequestEngine
    assert ServiceExpenseEngine
''',
    )


def gen_seeds() -> None:
    w(
        ALEMBIC / "0287_seed_service_permissions.py",
        '''"""Seed service permissions and roles."""

import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.service.permissions import (
    SERVICE_ADMIN_PERMISSIONS,
    SERVICE_COORDINATOR_PERMISSIONS,
    SERVICE_ENGINEER_PERMISSIONS,
    SERVICE_MANAGER_PERMISSIONS,
    SERVICE_PERMISSIONS,
)

revision: str = "0287_seed_service_permissions"
down_revision: str | None = "0286_svc_service_report"
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
    ("SERVICE_MANAGER", "Service Manager", SERVICE_MANAGER_PERMISSIONS),
    ("SERVICE_ENGINEER", "Service Engineer", SERVICE_ENGINEER_PERMISSIONS),
    ("SERVICE_COORDINATOR", "Service Coordinator", SERVICE_COORDINATOR_PERMISSIONS),
    ("SERVICE_ADMIN", "Service Admin", SERVICE_ADMIN_PERMISSIONS),
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
    for code, resource, action, module in SERVICE_PERMISSIONS:
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
    for code, _, _, _ in SERVICE_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM foundation.sec_permission WHERE permission_code = :code"),
            {"code": code},
        )
''',
    )

    w(
        ALEMBIC / "0288_seed_service_workflows.py",
        '''"""Seed service workflow definitions per ERD_16."""

from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "0288_seed_service_workflows"
down_revision: str | None = "0287_seed_service_permissions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WORKFLOWS: list[tuple[str, str, str, list[tuple[int, str, str, str]]]] = [
    (
        "SVC_REQUEST_APPROVAL",
        "Service Request Approval",
        "svc_service_request",
        [
            (1, "SERVICE_COORDINATOR", "Coordinator Submit", "role"),
            (2, "SERVICE_MANAGER", "Service Manager Approval", "role"),
        ],
    ),
    (
        "SVC_WORK_ORDER_APPROVAL",
        "Service Work Order Approval",
        "svc_service_work_order",
        [
            (1, "SERVICE_COORDINATOR", "Coordinator Submit", "role"),
            (2, "SERVICE_MANAGER", "Service Manager Approval", "role"),
        ],
    ),
    (
        "SVC_COMPLETION_APPROVAL",
        "Service Completion Approval",
        "svc_service_resolution",
        [
            (1, "SERVICE_ENGINEER", "Engineer Submit", "role"),
            (2, "SERVICE_MANAGER", "Service Manager Approval", "role"),
        ],
    ),
    (
        "SVC_SLA_ESCALATION",
        "Service SLA Escalation",
        "svc_service_escalation",
        [
            (1, "SERVICE_ENGINEER", "Agent Escalation", "role"),
            (2, "SERVICE_COORDINATOR", "Supervisor Escalation", "role"),
            (3, "SERVICE_MANAGER", "Manager Escalation", "role"),
        ],
    ),
    (
        "SVC_CONTRACT_APPROVAL",
        "Service Contract Approval",
        "svc_service_contract",
        [
            (1, "SERVICE_MANAGER", "Service Manager Submit", "role"),
            (2, "SERVICE_ADMIN", "Service Admin Approval", "role"),
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
                        (id, tenant_id, workflow_code, workflow_name, document_type,
                         version_no, is_active, is_parallel, status,
                         created_at, updated_at, is_deleted, version)
                        VALUES
                        (:id, :tid, :code, :name, :dtype,
                         1, true, false, 'active',
                         :now, :now, false, 1)
                        """
                    ),
                    {
                        "id": wf_id,
                        "tid": tid,
                        "code": workflow_code,
                        "name": workflow_name,
                        "dtype": document_type,
                        "now": now,
                    },
                )
            for step_no, role_code, step_name, assignee_type in steps:
                step_exists = conn.execute(
                    sa.text(
                        """
                        SELECT 1 FROM foundation.wf_step
                        WHERE definition_id = :wid AND step_no = :sno
                        """
                    ),
                    {"wid": wf_id, "sno": step_no},
                ).first()
                if step_exists:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO foundation.wf_step
                        (id, tenant_id, definition_id, step_no, step_name,
                         assignee_type, assignee_role_code, status,
                         created_at, updated_at, is_deleted, version)
                        VALUES
                        (:id, :tid, :wid, :sno, :sname,
                         :atype, :role, 'active',
                         :now, :now, false, 1)
                        """
                    ),
                    {
                        "id": str(uuid4()),
                        "tid": tid,
                        "wid": wf_id,
                        "sno": step_no,
                        "sname": step_name,
                        "atype": assignee_type,
                        "role": role_code,
                        "now": now,
                    },
                )


def downgrade() -> None:
    conn = op.get_bind()
    for workflow_code, _, _, _ in reversed(WORKFLOWS):
        conn.execute(
            sa.text(
                """
                DELETE FROM foundation.wf_step
                WHERE definition_id IN (
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
        "from modules.asset.router import asset_router\n",
        "from modules.asset.router import asset_router\n"
        "from modules.service.router import service_router\n",
    )
    patch_file(
        SHARED / "router.py",
        "api_v1_router.include_router(asset_router)\n",
        "api_v1_router.include_router(asset_router)\n"
        "api_v1_router.include_router(service_router)\n",
    )
    patch_file(
        ROOT / "alembic" / "env.py",
        "import modules.asset.models  # noqa: F401 — register ORM metadata\n",
        "import modules.asset.models  # noqa: F401 — register ORM metadata\n"
        "import modules.service.models  # noqa: F401 — register ORM metadata\n",
    )
    patch_file(
        ROOT / "src" / "workers" / "celery_app.py",
        '        "modules.asset",\n',
        '        "modules.asset",\n        "modules.service",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '    "modules.asset.*",\n',
        '    "modules.asset.*",\n    "modules.service.*",\n',
    )
    patch_file(
        ROOT / "pyproject.toml",
        '"src/modules/asset/**" = ["E501", "SIM102"]\n'
        '"src/modules/asset/domain/enums.py" = ["UP042"]\n',
        '"src/modules/asset/**" = ["E501", "SIM102"]\n'
        '"src/modules/asset/domain/enums.py" = ["UP042"]\n'
        '"src/modules/service/**" = ["E501", "SIM102"]\n'
        '"src/modules/service/domain/enums.py" = ["UP042"]\n',
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
    print(f"OK service module generated — {len(FILES_WRITTEN)} files")
    print("Alembic head revision: 0288_seed_service_workflows")


if __name__ == "__main__":
    main()
