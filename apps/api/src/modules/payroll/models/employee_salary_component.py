"""Employee salary component override ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayEmployeeSalaryComponent(Base, *PayTransactionMixin):
    __tablename__ = "pay_employee_salary_component"
    __table_args__ = (
        UniqueConstraint(
            "employee_salary_id",
            "salary_component_id",
            name="uk_pay_emp_sal_comp",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_emp_sal_comp_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    employee_salary_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_employee_salary.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    salary_component_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    percent: Mapped[Decimal | None] = mapped_column(Numeric(9, 4), nullable=True)
    override_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
