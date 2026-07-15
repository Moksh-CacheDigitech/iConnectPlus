"""Monitor ORM per ERD_21 section 5.19."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntMonitor(Base, *IntRowMixin):
    __tablename__ = "int_monitor"
    __table_args__ = (
        UniqueConstraint("company_id", "monitor_code", name="uk_int_monitor_code"),
        CheckConstraint(
            "check_type IN ('heartbeat','latency','error_rate','queue_depth')",
            name="ck_int_monitor_check_type",
        ),
        CheckConstraint(
            "status IN ('healthy','degraded','down','unknown','inactive')",
            name="ck_int_monitor_status",
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

    monitor_code: Mapped[str] = mapped_column(String(50), nullable=False)
    monitor_name: Mapped[str] = mapped_column(String(255), nullable=False)

    external_system_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_external_system.id",
            ondelete="SET NULL",
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
    check_type: Mapped[str] = mapped_column(String(30), nullable=False)
    threshold_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown", index=True)
