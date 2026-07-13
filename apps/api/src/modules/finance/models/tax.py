"""Tax register ORM model."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.finance.models.mixins import FinancePostedLedgerMixin


class FinTaxRegister(Base, *FinancePostedLedgerMixin):
    __tablename__ = "fin_tax_register"
    __table_args__ = (
        UniqueConstraint("company_id", "register_number", name="uk_fin_tax_register_company_number"),
        CheckConstraint(
            "tax_type IN ('gst','vat','sales_tax','withholding')",
            name="ck_fin_tax_register_tax_type",
        ),
        CheckConstraint(
            "transaction_type IN ('output','input','withheld','adjustment')",
            name="ck_fin_tax_register_transaction_type",
        ),
        CheckConstraint(
            "status IN ('active','reversed')",
            name="ck_fin_tax_register_status",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    register_number: Mapped[str] = mapped_column(String(50), nullable=False)
    register_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    tax_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_tax.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    tax_type: Mapped[str] = mapped_column(String(30), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    taxable_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    journal_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    journal_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=True,
    )
    vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
    )
    source_module: Mapped[str] = mapped_column(String(50), nullable=False)
    source_document_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
