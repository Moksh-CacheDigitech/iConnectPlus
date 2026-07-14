"""Project phase ORM per ERD_14 §6.2."""

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
        {"schema": "project"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

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
