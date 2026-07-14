"""HR goal ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrDetailMixin


class HrGoal(Base, *HrDetailMixin):
    __tablename__ = "hr_goal"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open','achieved','missed','cancelled')",
            name="ck_hr_goal_status",
        ),
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
    goal_title: Mapped[str] = mapped_column(String(255), nullable=False)
    goal_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    actual_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    weight_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
