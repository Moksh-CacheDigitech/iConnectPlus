"""Interview ORM per ERD_13 §6.8."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecInterview(Base, *RecTransactionMixin):
    __tablename__ = "rec_interview"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_intv_company_doc"),
        CheckConstraint(
            "interview_type IN ('hr_round','technical','manager','final','other')",
            name="ck_rec_intv_type",
        ),
        CheckConstraint(
            "result IN ('pending','pass','fail','hold')",
            name="ck_rec_intv_result",
        ),
        CheckConstraint(
            "status IN ('scheduled','completed','cancelled','no_show')",
            name="ck_rec_intv_status",
        ),
        {"schema": "recruitment"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    interview_type: Mapped[str] = mapped_column(String(30), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meeting_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    interviewer_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    panel_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled", index=True)
