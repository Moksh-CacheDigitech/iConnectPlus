"""Candidate pre-master ORM per ERD_13 §6.3."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecCandidate(Base, *RecMasterMixin):
    __tablename__ = "rec_candidate"
    __table_args__ = (
        UniqueConstraint("company_id", "candidate_code", name="uk_rec_candidate_company_code"),
        CheckConstraint(
            "status IN ('prospect','applied','screening','interview','selected','offered','hired','rejected','on_hold','withdrawn','blacklisted')",
            name="ck_rec_candidate_status",
        ),
        {"schema": "recruitment"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    candidate_code: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    mobile: Mapped[str | None] = mapped_column(String(30), nullable=True)
    current_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_employer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_experience_years: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    highest_education: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recruitment_source_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_recruitment_source.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    primary_recruiter_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_recruiter.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="prospect", index=True)
