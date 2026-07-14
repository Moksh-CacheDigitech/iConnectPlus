"""Payroll summary aggregate ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayPayrollSummary(Base, *PayMasterMixin):
    __tablename__ = "pay_payroll_summary"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_pay_summary_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    payroll_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_run.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payroll_period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    employee_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_gross: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_deduction: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_net: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_employer_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    summary_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
