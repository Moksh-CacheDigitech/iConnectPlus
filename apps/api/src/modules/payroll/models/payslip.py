"""Payslip ORM."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayPayslip(Base, *PayTransactionMixin):
    __tablename__ = "pay_payslip"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_payslip_company_doc"),
        CheckConstraint(
            "delivery_status IN ('pending','emailed','viewed','failed')",
            name="ck_pay_payslip_delivery",
        ),
        CheckConstraint(
            "payment_status IN ('unpaid','processing','paid','failed')",
            name="ck_pay_payslip_payment",
        ),
        CheckConstraint(
            "status IN ('generated','issued','void')",
            name="ck_pay_payslip_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    payroll_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_run_line_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run_line.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    gross_salary: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    total_deductions: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    net_salary: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    payslip_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    issued_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    payment_status: Mapped[str] = mapped_column(String(30), nullable=False, default="unpaid")
    bank_export_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="generated", index=True)
