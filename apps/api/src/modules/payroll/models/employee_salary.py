"""Employee salary assignment ORM."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayEmployeeSalary(Base, *PayTransactionMixin):
    __tablename__ = "pay_employee_salary"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_esal_company_doc"),
        CheckConstraint(
            "status IN ('draft','active','ended','cancelled')",
            name="ck_pay_esal_status",
        ),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    salary_structure_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_salary_structure.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    employment_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    department_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    ctc_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
