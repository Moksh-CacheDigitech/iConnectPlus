"""Project risk ORM per ERD_14 §6.14."""

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
