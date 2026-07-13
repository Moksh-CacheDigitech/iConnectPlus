"""Sales return ORM models."""

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


class SalesReturnHeader(Base, *SalesTransactionMixin):
    __tablename__ = "sales_return_header"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_sales_rh_company_number"),
        CheckConstraint(
            "return_type IN ('damaged','wrong_item','excess_qty','quality_issue')",
            name="ck_sales_rh_return_type",
        ),
        CheckConstraint(
            "status IN "
            "('draft','requested','approved','received','posted','closed','cancelled')",
            name="ck_sales_rh_status",
        ),
        CheckConstraint(
            "workflow_status IN ('pending','in_progress','approved','rejected')",
            name="ck_sales_rh_workflow_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
    )
    invoice_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_invoice_header.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    order_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_order_header.id", ondelete="RESTRICT"),
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
    )
    return_type: Mapped[str] = mapped_column(String(30), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    subtotal_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    lines: Mapped[list["SalesReturnLine"]] = relationship(
        back_populates="return_header",
        cascade="all, delete-orphan",
    )


class SalesReturnLine(Base, *SalesTransactionMixin):
    __tablename__ = "sales_return_line"
    __table_args__ = (
        UniqueConstraint("return_header_id", "line_number", name="uk_sales_rl_header_line"),
        CheckConstraint("quantity > 0", name="ck_sales_rl_qty"),
        CheckConstraint(
            "status IN ('requested','received','posted')",
            name="ck_sales_rl_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    return_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_return_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    invoice_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_invoice_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    order_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_order_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=False,
    )
    unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    tax_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_tax.id", ondelete="RESTRICT"),
        nullable=True,
    )
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    line_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="requested")

    return_header: Mapped[SalesReturnHeader] = relationship(back_populates="lines")
