"""HR performance review ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrPerformanceReview(Base, *HrTransactionMixin):
    __tablename__ = "hr_performance_review"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_hr_prf_company_doc"),
        CheckConstraint(
            "review_cycle IN ('monthly','quarterly','half_yearly','yearly')",
            name="ck_hr_prf_cycle",
        ),
        CheckConstraint(
            "status IN ('draft','in_progress','submitted','approved','closed','cancelled')",
            name="ck_hr_prf_status",
        ),
        CheckConstraint(
            "overall_rating IS NULL OR (overall_rating BETWEEN 1 AND 5)",
            name="ck_hr_prf_rating",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reviewer_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    review_cycle: Mapped[str] = mapped_column(String(30), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
    overall_rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
