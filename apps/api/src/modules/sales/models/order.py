"""Sales order ORM models."""

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
from modules.sales.models.mixins import SalesTransactionMixin


class SalesOrderHeader(Base, *SalesTransactionMixin):
    __tablename__ = "sales_order_header"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_sales_oh_company_number"),
        CheckConstraint(
            "status IN "
            "('draft','confirmed','processing','partially_delivered',"
            "'delivered','closed','cancelled')",
            name="ck_sales_oh_status",
        ),
        CheckConstraint(
            "workflow_status IN ('pending','in_progress','approved','rejected')",
            name="ck_sales_oh_workflow_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    requested_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quotation_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_quotation_header.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    price_list_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_price_list.id", ondelete="RESTRICT"),
        nullable=True,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    subtotal_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    delivered_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    invoiced_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    reservation_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_document_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    lines: Mapped[list["SalesOrderLine"]] = relationship(
        back_populates="order_header",
        cascade="all, delete-orphan",
    )


class SalesOrderLine(Base, *SalesTransactionMixin):
    __tablename__ = "sales_order_line"
    __table_args__ = (
        UniqueConstraint("order_header_id", "line_number", name="uk_sales_ol_header_line"),
        CheckConstraint("quantity > 0", name="ck_sales_ol_qty"),
        CheckConstraint(
            "status IN ('open','partially_delivered','delivered','cancelled')",
            name="ck_sales_ol_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_order_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    quotation_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_quotation_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    quantity_delivered: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    quantity_invoiced: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    quantity_returned: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=False,
    )
    unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    discount_percent: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_tax.id", ondelete="RESTRICT"),
        nullable=True,
    )
    tax_rate: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    line_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")

    order_header: Mapped[SalesOrderHeader] = relationship(back_populates="lines")
