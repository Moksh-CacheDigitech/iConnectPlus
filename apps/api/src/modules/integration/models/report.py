"""Integration report ORM per ERD_21 section 5.20."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.integration.models.mixins import IntRowMixin


class IntReport(Base, *IntRowMixin):
    __tablename__ = "int_report"
    __table_args__ = (
        UniqueConstraint("company_id", "report_code", name="uk_int_report_code"),
        CheckConstraint(
            "report_type IN ('delivery_success','dlq_aging','sync_performance',"
            "'api_usage','rate_limit_breaches','connector_health')",
            name="ck_int_report_type",
        ),
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_int_report_status",
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

    report_code: Mapped[str] = mapped_column(String(50), nullable=False)
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)

    external_system_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "integration.int_external_system.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
