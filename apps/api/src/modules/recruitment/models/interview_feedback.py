"""Interview feedback ORM per ERD_13 §6.9."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecInterviewFeedback(Base, *RecDetailMixin):
    __tablename__ = "rec_interview_feedback"
    __table_args__ = (
        UniqueConstraint(
            "interview_id",
            "interviewer_employee_id",
            name="uk_rec_intv_feedback_interviewer",
        ),
        CheckConstraint(
            "recommendation IN ('strong_hire','hire','no_hire','hold')",
            name="ck_rec_intv_feedback_recommendation",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','locked')",
            name="ck_rec_intv_feedback_status",
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

    interview_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_interview.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    interviewer_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    overall_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(String(30), nullable=True)
    competency_scores_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
