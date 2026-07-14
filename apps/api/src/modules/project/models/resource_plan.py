"""Resource plan ORM per ERD_14 §6.9."""

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
        {"schema": "project"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

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
