"""HR training attendance ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrTrainingAttendance(Base, *HrTransactionMixin):
    __tablename__ = "hr_training_attendance"
    __table_args__ = (
        UniqueConstraint("training_id", "employee_id", name="uk_hr_trn_att_training_emp"),
        CheckConstraint(
            "attendance_status IN ('registered','attended','absent','completed')",
            name="ck_hr_trn_att_day",
        ),
        CheckConstraint("status IN ('active','cancelled')", name="ck_hr_trn_att_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    training_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hr.hr_training.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    attendance_status: Mapped[str] = mapped_column(String(30), nullable=False, default="registered")
    completion_percent: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    certificate_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
