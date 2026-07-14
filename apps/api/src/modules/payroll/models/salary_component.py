"""Salary component catalog ORM."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PaySalaryComponent(Base, *PayMasterMixin):
    __tablename__ = "pay_salary_component"
    __table_args__ = (
        UniqueConstraint("company_id", "component_code", name="uk_pay_comp_company_code"),
        CheckConstraint(
            "component_class IN ('earning','deduction','employer_contribution')",
            name="ck_pay_comp_class",
        ),
        CheckConstraint(
            "calculation_method IN ('fixed','percentage','formula')",
            name="ck_pay_comp_calc",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_comp_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    component_code: Mapped[str] = mapped_column(String(50), nullable=False)
    component_name: Mapped[str] = mapped_column(String(255), nullable=False)
    component_class: Mapped[str] = mapped_column(String(30), nullable=False)
    earning_type_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_earning_type.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    deduction_type_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_deduction_type.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    calculation_method: Mapped[str] = mapped_column(String(30), nullable=False, default="fixed")
    percentage_base_component_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_component.id", ondelete="RESTRICT"),
        nullable=True,
    )
    is_taxable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_statutory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    gl_expense_account_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    gl_liability_account_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
