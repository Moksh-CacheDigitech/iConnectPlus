"""Inventory reservation ORM model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.inventory.models.mixins import InvTransactionMixin


class InvReservation(Base, *InvTransactionMixin):
    __tablename__ = "inv_reservation"
    __table_args__ = (
        CheckConstraint("quantity_reserved > 0", name="ck_inv_res_qty"),
        CheckConstraint("quantity_issued >= 0", name="ck_inv_res_issued"),
        CheckConstraint(
            "status IN ('active','partially_issued','fulfilled','released','cancelled')",
            name="ck_inv_res_status",
        ),
        Index(
            "ix_inv_res_source",
            "source_module",
            "source_document_type",
            "source_document_id",
        ),
        Index("ix_inv_res_status", "status"),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_warehouse.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
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
    quantity_reserved: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    quantity_issued: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    source_module: Mapped[str] = mapped_column(String(50), nullable=False)
    source_document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_document_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    source_line_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    reserved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
