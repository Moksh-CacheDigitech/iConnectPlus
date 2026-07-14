"""Loan ORM."""

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


class PayLoan(Base, *PayTransactionMixin):
    __tablename__ = "pay_loan"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_loan_company_doc"),
        CheckConstraint(
            "loan_type IN ('personal','salary_advance','emergency')",
            name="ck_pay_loan_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','closed','rejected','cancelled')",
            name="ck_pay_loan_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    loan_type: Mapped[str] = mapped_column(String(30), nullable=False)
    principal_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    emi_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False, default=0)
    installment_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
