"""Procurement purchase invoice ORM models."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.procurement.models.mixins import ProcTransactionMixin


class ProcInvoiceHeader(Base, *ProcTransactionMixin):
    __tablename__ = "proc_invoice_header"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_proc_ih_company_number"),
        UniqueConstraint(
            "company_id",
            "vendor_id",
            "vendor_invoice_number",
            name="uk_proc_ih_vendor_invoice",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','posted','partially_paid','paid','cancelled')",
            name="ck_proc_ih_status",
        ),
        CheckConstraint(
            "match_status IN ('unmatched','partial','matched','exception')",
            name="ck_proc_ih_match_status",
        ),
        CheckConstraint(
            "posting_status IN ('pending','posted','failed') OR posting_status IS NULL",
            name="ck_proc_ih_posting_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    vendor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    vendor_invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    order_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_order_header.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    grn_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_grn_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    fiscal_year_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_fiscal_year.id", ondelete="RESTRICT"),
        nullable=True,
    )
    period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_period.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    subtotal_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    amount_paid: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    balance_due: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    match_status: Mapped[str] = mapped_column(String(30), nullable=False, default="unmatched")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    finance_ledger_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_vendor_ledger.id", ondelete="RESTRICT"),
        nullable=True,
    )
    finance_journal_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    posting_status: Mapped[str | None] = mapped_column(String(30), nullable=True)

    lines: Mapped[list["ProcInvoiceLine"]] = relationship(
        back_populates="invoice_header",
        cascade="all, delete-orphan",
    )


class ProcInvoiceLine(Base, *ProcTransactionMixin):
    __tablename__ = "proc_invoice_line"
    __table_args__ = (
        UniqueConstraint("invoice_header_id", "line_number", name="uk_proc_il_header_line"),
        CheckConstraint("quantity > 0", name="ck_proc_il_qty"),
        CheckConstraint(
            "status IN ('open','posted','cancelled')",
            name="ck_proc_il_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_invoice_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_order_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    grn_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_grn_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=False,
    )
    unit_cost: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    tax_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_tax.id", ondelete="RESTRICT"),
        nullable=True,
    )
    tax_rate: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    line_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    expense_account_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_chart_of_account.id", ondelete="RESTRICT"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")

    invoice_header: Mapped[ProcInvoiceHeader] = relationship(back_populates="lines")
