"""Customer expense ledger - FOC material, visits and favours to recover later."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.crm.models.mixins import CrmTransactionMixin


class CrmCustomerExpense(Base, *CrmTransactionMixin):
    __tablename__ = "crm_customer_expense"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_crm_customer_expense_amount"),
        CheckConstraint(
            "category IN ('foc_material','replacement','site_visit','service','cables','other')",
            name="ck_crm_customer_expense_category",
        ),
        CheckConstraint(
            "status IN ('open','adjusted','written_off')",
            name="ck_crm_customer_expense_status",
        ),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm.crm_company.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    opportunity_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm.crm_opportunity.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    approved_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approval_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    adjust_in_future: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", server_default="open")
    adjusted_ovf_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm.crm_ovf.id", ondelete="RESTRICT"),
        nullable=True,
    )
    adjusted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    adjustment_remark: Mapped[str | None] = mapped_column(Text, nullable=True)
