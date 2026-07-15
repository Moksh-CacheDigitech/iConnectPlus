"""Shipping tracking ORM per ERD_22 section 5.13."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcShippingTracking(Base, *EcRowMixin):
    __tablename__ = "ec_shipping_tracking"
    __table_args__ = (
        CheckConstraint(
            "tracking_status IN ('created','picked_up','in_transit','out_for_delivery',"
            "'delivered','exception','returned_to_seller')",
            name="ck_ec_shipping_tracking_status",
        ),
        CheckConstraint(
            "status IN ('recorded')",
            name="ck_ec_shipping_tracking_row_status",
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


    shipment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_shipment.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    tracked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    tracking_status: Mapped[str] = mapped_column(String(40), nullable=False)
    location_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    carrier_event_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
