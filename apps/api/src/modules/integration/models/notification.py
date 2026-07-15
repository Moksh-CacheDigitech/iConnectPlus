"""Integration notification ORM per ERD_21 section 5.18."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntNotification(Base, *IntRowMixin):
    __tablename__ = "int_notification"
    __table_args__ = (
        CheckConstraint(
            "related_entity_type IN ('connector','webhook','sync','retry','dlq','credential','monitor')",
            name="ck_int_notification_entity_type",
        ),
        CheckConstraint(
            "notification_type IN ('sync_failed','dlq_created','credential_expiring',"
            "'rate_limit_hit','monitor_down','other')",
            name="ck_int_notification_type",
        ),
        CheckConstraint(
            "delivery_status IN ('pending','sent','failed','read')",
            name="ck_int_notification_delivery",
        ),
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_int_notification_status",
        ),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )


    connector_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_connector.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    related_entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    related_entity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    notification_type: Mapped[str] = mapped_column(String(40), nullable=False)

    recipient_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    recipient_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
