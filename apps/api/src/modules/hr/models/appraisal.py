"""HR appraisal ORM."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrDetailMixin


class HrAppraisal(Base, *HrDetailMixin):
    __tablename__ = "hr_appraisal"
    __table_args__ = (
        CheckConstraint(
            "appraisal_area IN ('goals','kpi','competency','behavior','attendance')",
            name="ck_hr_appr_area",
        ),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_hr_appr_rating"),
        CheckConstraint("status IN ('draft','final')", name="ck_hr_appr_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    performance_review_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_performance_review.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    appraisal_area: Mapped[str] = mapped_column(String(30), nullable=False)
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
