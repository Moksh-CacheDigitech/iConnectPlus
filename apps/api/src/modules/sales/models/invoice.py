"""Invoice ORM models."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.sales.models.mixins import SalesTransactionMixin


class SalesInvoiceHeader(Base, *SalesTransactionMixin):
    __tablename__ = "sales_invoice_header"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_sales_ih_company_number"),
        CheckConstraint("total_amount >= 0", name="ck_sales_ih_amounts"),
        CheckConstraint(
            "status IN "
            "('draft','submitted','posted','partially_paid','paid','cancelled')",
            name="ck_sales_ih_status",
        ),
        CheckConstraint(
            "workflow_status IN ('pending','in_progress','approved','rejected')",
            name="ck_sales_ih_workflow_status",
        ),
        CheckConstraint("due_date >= document_date", name="ck_sales_ih_due_date"),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_order_header.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    delivery_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_delivery_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    fiscal_year_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_fiscal_year.id", ondelete="RESTRICT"),
        nullable=False,
    )
    period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_period.id", ondelete="RESTRICT"),
        nullable=False,
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
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.sec_user.id", ondelete="RESTRICT"),
        nullable=True,
    )
    finance_ledger_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_customer_ledger.id", ondelete="RESTRICT"),
        nullable=True,
    )
    finance_journal_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    posting_status: Mapped[str | None] = mapped_column(String(30), nullable=True)

    lines: Mapped[list["SalesInvoiceLine"]] = relationship(
        back_populates="invoice_header",
        cascade="all, delete-orphan",
    )


class SalesInvoiceLine(Base, *SalesTransactionMixin):
    __tablename__ = "sales_invoice_line"
    __table_args__ = (
        UniqueConstraint("invoice_header_id", "line_number", name="uk_sales_il_header_line"),
        CheckConstraint("quantity > 0", name="ck_sales_il_qty"),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    invoice_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_invoice_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_order_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    delivery_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_delivery_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=False,
    )
    unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_tax.id", ondelete="RESTRICT"),
        nullable=True,
    )
    tax_rate: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    line_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    revenue_account_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_chart_of_account.id", ondelete="RESTRICT"),
        nullable=True,
    )

    invoice_header: Mapped[SalesInvoiceHeader] = relationship(back_populates="lines")
