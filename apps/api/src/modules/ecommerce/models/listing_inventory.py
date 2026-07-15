"""Listing inventory ORM per ERD_22 section 5.5."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcListingInventory(Base, *EcRowMixin):
    __tablename__ = "ec_listing_inventory"
    __table_args__ = (
        CheckConstraint(
            "sync_status IN ('in_sync','pending','failed','stale')",
            name="ck_ec_listing_inventory_sync_status",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_ec_listing_inventory_status",
        ),
        {"schema": "ecommerce"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )


    product_listing_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_product_listing.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    warehouse_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    available_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    reserved_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    safety_stock_qty: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    last_synced_at: Mapped[datetime | None] = mapped_column(nullable=True)

    inventory_item_ref_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    sync_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
