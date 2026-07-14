"""Statutory contribution rate ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayStatutoryContribution(Base, *PayMasterMixin):
    __tablename__ = "pay_statutory_contribution"
    __table_args__ = (
        UniqueConstraint("company_id", "contribution_code", name="uk_pay_stat_contrib_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_stat_contrib_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    contribution_code: Mapped[str] = mapped_column(String(50), nullable=False)
    contribution_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_rate_percent: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False)
    employer_rate_percent: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False)
    wage_ceiling_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary_component_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
