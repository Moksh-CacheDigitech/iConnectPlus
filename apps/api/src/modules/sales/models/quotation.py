"""Quotation ORM models."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.sales.models.mixins import SalesTransactionMixin


class SalesQuotationHeader(Base, *SalesTransactionMixin):
    __tablename__ = "sales_quotation_header"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_sales_qh_company_number"),
        CheckConstraint(
            "status IN "
            "('draft','submitted','sent','accepted','rejected','expired','cancelled')",
            name="ck_sales_qh_status",
        ),
        CheckConstraint(
            "workflow_status IN ('pending','in_progress','approved','rejected')",
            name="ck_sales_qh_workflow_status",
        ),
        CheckConstraint("valid_until >= document_date", name="ck_sales_qh_valid_until"),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    payment_terms: Mapped[str | None] = mapped_column(String(100), nullable=True)
    opportunity_reference: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    price_list_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_price_list.id", ondelete="RESTRICT"),
        nullable=True,
    )
    subtotal_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    lines: Mapped[list["SalesQuotationLine"]] = relationship(
        back_populates="quotation_header",
        cascade="all, delete-orphan",
    )


class SalesQuotationLine(Base, *SalesTransactionMixin):
    __tablename__ = "sales_quotation_line"
    __table_args__ = (
        UniqueConstraint(
            "quotation_header_id",
            "line_number",
            name="uk_sales_ql_header_line",
        ),
        CheckConstraint("quantity > 0", name="ck_sales_ql_qty"),
        CheckConstraint("unit_price >= 0", name="ck_sales_ql_price"),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    quotation_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_quotation_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
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

    quotation_header: Mapped[SalesQuotationHeader] = relationship(back_populates="lines")
