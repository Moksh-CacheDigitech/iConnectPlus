"""Salary structure line ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayDetailMixin


class PaySalaryStructureLine(Base, *PayDetailMixin):
    __tablename__ = "pay_salary_structure_line"
    __table_args__ = (
        UniqueConstraint(
            "salary_structure_id",
            "salary_component_id",
            name="uk_pay_struct_line_comp",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_struct_line_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    salary_structure_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_structure.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    salary_component_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_no: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    default_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    default_percent: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
