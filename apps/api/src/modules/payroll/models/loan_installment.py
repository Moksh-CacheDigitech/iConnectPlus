"""Loan installment schedule ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayLoanInstallment(Base, *PayTransactionMixin):
    __tablename__ = "pay_loan_installment"
    __table_args__ = (
        UniqueConstraint("loan_id", "installment_no", name="uk_pay_loan_inst_no"),
        CheckConstraint(
            "status IN ('scheduled','recovered','waived','overdue','cancelled')",
            name="ck_pay_loan_inst_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    loan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_loan.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    installment_no: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payroll_period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    due_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    payroll_run_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run_line.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled", index=True)
