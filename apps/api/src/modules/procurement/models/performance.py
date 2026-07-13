"""Procurement vendor performance ORM model."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.procurement.models.mixins import ProcMasterMixin


class ProcVendorPerformance(Base, *ProcMasterMixin):
    __tablename__ = "proc_vendor_performance"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "vendor_id", "period_code", name="uk_proc_vp_company_vendor_period"
        ),
        CheckConstraint(
            "overall_score >= 0 AND overall_score <= 100",
            name="ck_proc_vp_overall_score",
        ),
        CheckConstraint(
            "status IN ('current','superseded')",
            name="ck_proc_vp_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
    )
    vendor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    period_code: Mapped[str] = mapped_column(String(20), nullable=False)
    on_time_delivery_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    quality_rating: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    cost_competitiveness_score: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    contract_compliance_score: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    issue_resolution_days: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    overall_score: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="current")
