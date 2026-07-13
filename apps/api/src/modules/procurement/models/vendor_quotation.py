"""Procurement vendor quotation and comparison ORM models."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.procurement.models.mixins import ProcTransactionMixin


class ProcVendorQuotationHeader(Base, *ProcTransactionMixin):
    __tablename__ = "proc_vendor_quotation_header"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "document_number", name="uk_proc_vqh_company_number"
        ),
        CheckConstraint(
            "status IN ('draft','submitted','under_review','selected','rejected','expired')",
            name="ck_proc_vqh_status",
        ),
        CheckConstraint(
            "valid_until >= document_date",
            name="ck_proc_vqh_valid_until",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    rfq_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_rfq_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    vendor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    vendor_quote_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    payment_terms: Mapped[str | None] = mapped_column(String(100), nullable=True)
    delivery_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    subtotal_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    attachment_reference: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    lines: Mapped[list["ProcVendorQuotationLine"]] = relationship(
        back_populates="quotation_header",
        cascade="all, delete-orphan",
    )


class ProcVendorQuotationLine(Base, *ProcTransactionMixin):
    __tablename__ = "proc_vendor_quotation_line"
    __table_args__ = (
        UniqueConstraint(
            "vendor_quotation_header_id", "line_number", name="uk_proc_vql_header_line"
        ),
        CheckConstraint("quantity > 0", name="ck_proc_vql_qty"),
        CheckConstraint("unit_cost > 0", name="ck_proc_vql_unit_cost"),
        CheckConstraint(
            "status IN ('active','rejected')",
            name="ck_proc_vql_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_quotation_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_vendor_quotation_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    rfq_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_rfq_line.id", ondelete="RESTRICT"),
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
    unit_cost: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tax_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_tax.id", ondelete="RESTRICT"),
        nullable=True,
    )
    tax_rate: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    line_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    is_alternate_product: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    quotation_header: Mapped[ProcVendorQuotationHeader] = relationship(back_populates="lines")


class ProcVendorComparison(Base, *ProcTransactionMixin):
    __tablename__ = "proc_vendor_comparison"
    __table_args__ = (
        UniqueConstraint("rfq_header_id", name="uk_proc_vc_rfq"),
        CheckConstraint(
            "status IN ('draft','completed')",
            name="ck_proc_vc_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rfq_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_rfq_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    best_price_quotation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_vendor_quotation_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    best_delivery_quotation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_vendor_quotation_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    best_overall_quotation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_vendor_quotation_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    selected_quotation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_vendor_quotation_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    score_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    compared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
