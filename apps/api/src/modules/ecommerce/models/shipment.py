"""Shipment ORM per ERD_22 section 5.12."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcShipment(Base, *EcRowMixin):
    __tablename__ = "ec_shipment"
    __table_args__ = (
        UniqueConstraint("company_id", "shipment_number", name="uk_ec_shipment_number"),
        CheckConstraint(
            "carrier_code IN ('shiprocket','delhivery','bluedart','fedex','dhl','other')",
            name="ck_ec_shipment_carrier",
        ),
        CheckConstraint(
            "status IN ('pending','packed','shipped','in_transit','delivered','cancelled','failed')",
            name="ck_ec_shipment_status",
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

    shipment_number: Mapped[str] = mapped_column(String(50), nullable=False)

    order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_order.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    carrier_code: Mapped[str] = mapped_column(String(40), nullable=False, default="other")
    tracking_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(nullable=True)
    shipping_label_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)

    sales_delivery_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
