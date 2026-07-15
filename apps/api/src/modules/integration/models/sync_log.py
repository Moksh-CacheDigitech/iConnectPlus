"""Sync log ORM per ERD_21 section 5.15."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntSyncLog(Base, *IntRowMixin):
    __tablename__ = "int_sync_log"
    __table_args__ = (
        CheckConstraint(
            "level IN ('info','warn','error')",
            name="ck_int_sync_log_level",
        ),
        CheckConstraint("status IN ('recorded')", name="ck_int_sync_log_status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    sync_job_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_sync_job.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    logged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    level: Mapped[str] = mapped_column(String(10), nullable=False, default="info")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    entity_ref_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
