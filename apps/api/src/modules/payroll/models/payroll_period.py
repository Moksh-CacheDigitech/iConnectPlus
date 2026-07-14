"""Payroll period ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayPayrollPeriod(Base, *PayMasterMixin):
    __tablename__ = "pay_payroll_period"
    __table_args__ = (
        UniqueConstraint("company_id", "period_code", name="uk_pay_period_company_code"),
        CheckConstraint(
            "status IN ('open','processing','approved','closed','cancelled')",
            name="ck_pay_period_status",
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
    period_code: Mapped[str] = mapped_column(String(50), nullable=False)
    period_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payroll_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    payroll_month: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
