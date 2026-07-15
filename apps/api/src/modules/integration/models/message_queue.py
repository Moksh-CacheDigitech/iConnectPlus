"""Message queue ORM per ERD_21 section 5.8."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntMessageQueue(Base, *IntRowMixin):
    __tablename__ = "int_message_queue"
    __table_args__ = (
        UniqueConstraint("company_id", "queue_code", name="uk_int_message_queue_code"),
        CheckConstraint(
            "queue_type IN ('standard','fifo','priority')",
            name="ck_int_message_queue_type",
        ),
        CheckConstraint(
            "status IN ('active','paused','drained')",
            name="ck_int_message_queue_status",
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

    queue_code: Mapped[str] = mapped_column(String(50), nullable=False)
    queue_name: Mapped[str] = mapped_column(String(255), nullable=False)
    queue_type: Mapped[str] = mapped_column(String(30), nullable=False, default="standard")
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    visibility_timeout_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
