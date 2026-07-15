"""Event subscription ORM per ERD_21 section 5.7."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntEventSubscription(Base, *IntRowMixin):
    __tablename__ = "int_event_subscription"
    __table_args__ = (
        UniqueConstraint("company_id", "subscription_number", name="uk_int_event_sub_number"),
        CheckConstraint(
            "subscriber_type IN ('webhook','queue','connector','internal_handler')",
            name="ck_int_event_sub_type",
        ),
        CheckConstraint(
            "status IN ('active','paused','cancelled')",
            name="ck_int_event_sub_status",
        ),
        Index("ix_int_event_sub_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    subscription_number: Mapped[str] = mapped_column(String(50), nullable=False)
    event_definition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_event_definition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    subscriber_type: Mapped[str] = mapped_column(String(30), nullable=False)

    webhook_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_webhook.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    message_queue_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_message_queue.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_int_sub_queue",
        ),
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
    filter_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
