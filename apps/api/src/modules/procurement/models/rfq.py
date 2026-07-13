"""Procurement RFQ ORM models."""

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
from modules.procurement.models.mixins import ProcTransactionMixin


class ProcRfqHeader(Base, *ProcTransactionMixin):
    __tablename__ = "proc_rfq_header"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_proc_rfqh_company_number"),
        CheckConstraint(
            "status IN ('draft','published','quotes_received','closed','cancelled')",
            name="ck_proc_rfqh_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    requisition_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_requisition_header.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    closing_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    lines: Mapped[list["ProcRfqLine"]] = relationship(
        back_populates="rfq_header",
        cascade="all, delete-orphan",
    )
    vendors: Mapped[list["ProcRfqVendor"]] = relationship(
        back_populates="rfq_header",
        cascade="all, delete-orphan",
    )


class ProcRfqLine(Base, *ProcTransactionMixin):
    __tablename__ = "proc_rfq_line"
    __table_args__ = (
        UniqueConstraint("rfq_header_id", "line_number", name="uk_proc_rfql_header_line"),
        CheckConstraint("quantity > 0", name="ck_proc_rfql_qty"),
        CheckConstraint(
            "status IN ('open','closed','cancelled')",
            name="ck_proc_rfql_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    rfq_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_rfq_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    requisition_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_requisition_line.id", ondelete="RESTRICT"),
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
    target_unit_cost: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")

    rfq_header: Mapped[ProcRfqHeader] = relationship(back_populates="lines")


class ProcRfqVendor(Base, *ProcTransactionMixin):
    __tablename__ = "proc_rfq_vendor"
    __table_args__ = (
        UniqueConstraint("rfq_header_id", "vendor_id", name="uk_proc_rfqv_rfq_vendor"),
        CheckConstraint(
            "invite_status IN ('invited','notified','declined')",
            name="ck_proc_rfqv_invite_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
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
    invite_status: Mapped[str] = mapped_column(String(30), nullable=False, default="invited")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    rfq_header: Mapped[ProcRfqHeader] = relationship(back_populates="vendors")
