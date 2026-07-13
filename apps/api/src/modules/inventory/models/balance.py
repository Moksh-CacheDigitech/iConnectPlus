"""Inventory stock balance ORM model."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.inventory.models.mixins import InvTransactionMixin


class InvStockBalance(Base, *InvTransactionMixin):
    __tablename__ = "inv_stock_balance"
    __table_args__ = (
        CheckConstraint("on_hand_qty >= 0", name="ck_inv_sb_on_hand"),
        CheckConstraint("reserved_qty >= 0", name="ck_inv_sb_reserved"),
        CheckConstraint("available_qty >= 0", name="ck_inv_sb_available"),
        CheckConstraint(
            "quality_status IN ('available','quarantine','rejected')",
            name="ck_inv_sb_quality",
        ),
        CheckConstraint(
            "status IN ('active','blocked')",
            name="ck_inv_sb_status",
        ),
        Index(
            "ix_inv_sb_wh_product",
            "tenant_id",
            "company_id",
            "warehouse_id",
            "product_id",
        ),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_warehouse.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    bin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory.inv_bin.id", ondelete="RESTRICT"),
        nullable=True,
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
        index=True,
    )
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=False,
    )
    on_hand_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    reserved_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    available_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    quality_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="available"
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
