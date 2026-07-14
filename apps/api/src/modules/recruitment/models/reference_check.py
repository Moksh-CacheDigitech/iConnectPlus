"""Reference check ORM per ERD_13 §6.13."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecDetailMixin


class RecReferenceCheck(Base, *RecDetailMixin):
    __tablename__ = "rec_reference_check"
    __table_args__ = (
        CheckConstraint(
            "relationship IN ('manager','peer','client','academic','other')",
            name="ck_rec_ref_check_relationship",
        ),
        CheckConstraint(
            "status IN ('pending','contacted','completed','declined','cancelled')",
            name="ck_rec_ref_check_status",
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

    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    application_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reference_name: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_org: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reference_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reference_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    relationship: Mapped[str] = mapped_column(String(30), nullable=False)
    feedback_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checked_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
