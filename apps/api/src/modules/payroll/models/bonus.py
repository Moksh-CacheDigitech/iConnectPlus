"""Bonus ORM."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayTransactionMixin


class PayBonus(Base, *PayTransactionMixin):
    __tablename__ = "pay_bonus"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_pay_bonus_company_doc"),
        CheckConstraint(
            "bonus_type IN ('festival','performance','retention','other')",
            name="ck_pay_bonus_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','paid','rejected','cancelled')",
            name="ck_pay_bonus_status",
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
    payroll_period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("payroll.pay_payroll_period.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    bonus_type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
