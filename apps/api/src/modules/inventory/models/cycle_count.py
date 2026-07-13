"""Inventory cycle count ORM models."""

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
from modules.inventory.models.mixins import InvTransactionMixin


class InvCycleCountHeader(Base, *InvTransactionMixin):
    __tablename__ = "inv_cycle_count_header"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_inv_cch_company_number"),
        CheckConstraint(
            "count_type IN ('daily','weekly','monthly','annual')",
            name="ck_inv_cch_type",
        ),
        CheckConstraint(
            "status IN ("
            "'draft','in_progress','submitted','approved','posted','cancelled')"
            ,
            name="ck_inv_cch_status",
        ),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    count_type: Mapped[str] = mapped_column(String(30), nullable=False, default="monthly")
    warehouse_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_warehouse.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )

    lines: Mapped[list["InvCycleCountLine"]] = relationship(
        back_populates="cycle_count_header",
        cascade="all, delete-orphan",
    )


class InvCycleCountLine(Base, *InvTransactionMixin):
    __tablename__ = "inv_cycle_count_line"
    __table_args__ = (
        UniqueConstraint("cycle_count_header_id", "line_number", name="uk_inv_ccl_header_line"),
        CheckConstraint(
            "variance_type IN ('match','shortage','excess')",
            name="ck_inv_ccl_variance",
        ),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    cycle_count_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory.inv_cycle_count_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
    )
    bin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory.inv_bin.id", ondelete="RESTRICT"),
        nullable=True,
    )
    batch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory.inv_batch.id", ondelete="RESTRICT"),
        nullable=True,
    )
    system_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    counted_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    variance_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    variance_type: Mapped[str] = mapped_column(String(30), nullable=False, default="match")
    adjustment_line_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")

    cycle_count_header: Mapped[InvCycleCountHeader] = relationship(back_populates="lines")
