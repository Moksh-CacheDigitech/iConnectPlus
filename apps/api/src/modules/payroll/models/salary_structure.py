"""Salary structure catalog ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PaySalaryStructure(Base, *PayMasterMixin):
    __tablename__ = "pay_salary_structure"
    __table_args__ = (
        UniqueConstraint("company_id", "structure_code", name="uk_pay_struct_company_code"),
        CheckConstraint("status IN ('draft','active','inactive')", name="ck_pay_struct_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    structure_code: Mapped[str] = mapped_column(String(50), nullable=False)
    structure_name: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
