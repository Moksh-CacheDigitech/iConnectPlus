"""Notification ORM per ERD_22 section 5.19."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcNotification(Base, *EcRowMixin):
    __tablename__ = "ec_notification"
    __table_args__ = (
        CheckConstraint(
            "notification_type IN ('order_received','order_shipped','order_delivered',"
            "'return_requested','inventory_low','sync_failed','payment_failed','other')",
            name="ck_ec_notification_type",
        ),
        CheckConstraint(
            "channel IN ('email','sms','whatsapp','push','in_app')",
            name="ck_ec_notification_channel",
        ),
        CheckConstraint(
            "delivery_status IN ('pending','sent','failed','read')",
            name="ck_ec_notification_delivery_status",
        ),
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_ec_notification_status",
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


    sales_channel_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_sales_channel.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_order.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    return_request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_return_request.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    shipment_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_shipment.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(40), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), nullable=False, default="email")

    recipient_customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    recipient_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
