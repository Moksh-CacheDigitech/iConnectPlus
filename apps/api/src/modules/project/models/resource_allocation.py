"""Resource allocation ORM per ERD_14 §6.10."""

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
        {"schema": "project"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

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
