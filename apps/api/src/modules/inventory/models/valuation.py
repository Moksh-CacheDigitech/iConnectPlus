"""Inventory FIFO valuation layer ORM model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.inventory.models.mixins import InvTransactionMixin


class InvValuationLayer(Base, *InvTransactionMixin):
    __tablename__ = "inv_valuation_layer"
    __table_args__ = (
        CheckConstraint("original_qty > 0", name="ck_inv_vl_original"),
        CheckConstraint("remaining_qty >= 0", name="ck_inv_vl_remaining"),
        CheckConstraint("unit_cost >= 0", name="ck_inv_vl_cost"),
        CheckConstraint(
            "status IN ('open','depleted','reversed')",
            name="ck_inv_vl_status",
        ),
        Index(
            "ix_inv_vl_fifo",
            "company_id",
            "warehouse_id",
            "product_id",
            "received_at",
        ),
        Index("ix_inv_vl_status", "status"),
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
    batch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory.inv_batch.id", ondelete="RESTRICT"),
        nullable=True,
    )
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    original_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    remaining_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    source_module: Mapped[str] = mapped_column(String(50), nullable=False)
    source_document_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
