"""Message ORM per ERD_21 section 5.9."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntMessage(Base, *IntRowMixin):
    __tablename__ = "int_message"
    __table_args__ = (
        UniqueConstraint("company_id", "message_number", name="uk_int_message_number"),
        CheckConstraint(
            "status IN ('queued','processing','succeeded','failed','dead_lettered','cancelled')",
            name="ck_int_message_status",
        ),
        Index("ix_int_message_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    message_number: Mapped[str] = mapped_column(String(50), nullable=False)
    message_queue_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_message_queue.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    event_definition_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_event_definition.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    correlation_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_module: Mapped[str | None] = mapped_column(String(40), nullable=True)

    entity_ref_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    finance_event_ref_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    available_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="queued", index=True)
