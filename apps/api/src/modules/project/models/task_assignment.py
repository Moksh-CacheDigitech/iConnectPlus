"""Task assignment ORM per ERD_14 §6.6."""

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
        {"schema": "project"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

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
