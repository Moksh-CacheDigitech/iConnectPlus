"""Delivery ORM models."""

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
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.sales.models.mixins import SalesTransactionMixin


class SalesDeliveryHeader(Base, *SalesTransactionMixin):
    __tablename__ = "sales_delivery_header"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_sales_dh_company_number"),
        CheckConstraint(
            "status IN "
            "('draft','pending','in_progress','partially_delivered','delivered','cancelled')",
            name="ck_sales_dh_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    order_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_order_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ship_to_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    warehouse_reference: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    subtotal_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    shipped_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.sec_user.id", ondelete="RESTRICT"),
        nullable=True,
    )

    lines: Mapped[list["SalesDeliveryLine"]] = relationship(
        back_populates="delivery_header",
        cascade="all, delete-orphan",
    )


class SalesDeliveryLine(Base, *SalesTransactionMixin):
    __tablename__ = "sales_delivery_line"
    __table_args__ = (
        UniqueConstraint("delivery_header_id", "line_number", name="uk_sales_dl_header_line"),
        CheckConstraint("quantity > 0", name="ck_sales_dl_qty"),
        CheckConstraint(
            "status IN ('pending','shipped','cancelled')",
            name="ck_sales_dl_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    delivery_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_delivery_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_line_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_order_line.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
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
    batch_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")

    delivery_header: Mapped[SalesDeliveryHeader] = relationship(back_populates="lines")
