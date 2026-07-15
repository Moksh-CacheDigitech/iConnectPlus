"""Sync job ORM per ERD_21 section 5.14."""

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
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntSyncJob(Base, *IntRowMixin):
    __tablename__ = "int_sync_job"
    __table_args__ = (
        UniqueConstraint("company_id", "sync_number", name="uk_int_sync_job_number"),
        CheckConstraint(
            "sync_mode IN ('full','incremental','realtime')",
            name="ck_int_sync_job_mode",
        ),
        CheckConstraint(
            "direction IN ('pull','push','bidirectional')",
            name="ck_int_sync_job_direction",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','queued','running','succeeded','failed','cancelled')",
            name="ck_int_sync_job_status",
        ),
        Index("ix_int_sync_job_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "integration"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    sync_number: Mapped[str] = mapped_column(String(50), nullable=False)
    connector_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("integration.int_connector.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    mapping_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_data_mapping.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    sync_mode: Mapped[str] = mapped_column(String(30), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    schedule_cron: Mapped[str | None] = mapped_column(String(100), nullable=True)

    requested_by_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rows_processed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

