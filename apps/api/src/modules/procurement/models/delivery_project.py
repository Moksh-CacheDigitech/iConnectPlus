"""Multi-site delivery project: one customer programme, many sites / POs, one tracker."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.procurement.models.mixins import ProcTransactionMixin

DELIVERY_MILESTONE_CHECK = (
    "milestone IN ('order_placed','ready_at_factory','dispatched_from_factory','received_in_india',"
    "'received_at_warehouse','dispatched_to_site','reached_site','installed')"
)


class ProcDeliveryProject(Base, *ProcTransactionMixin):
    __tablename__ = "proc_delivery_project"
    __table_args__ = (
        CheckConstraint("status IN ('active','on_hold','completed')", name="ck_proc_dproj_status"),
        UniqueConstraint("company_id", "project_code", name="uk_proc_dproj_company_code"),
        UniqueConstraint("tracking_token", name="uk_proc_dproj_tracking_token"),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Soft links to crm.crm_company / crm.crm_opportunity - no cross-module FK.
    company_account_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    opportunity_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    # Unguessable key behind the customer's public tracking link.
    tracking_token: Mapped[str] = mapped_column(String(64), nullable=False)
    public_tracking_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProcDeliveryProjectSite(Base, *ProcTransactionMixin):
    __tablename__ = "proc_delivery_project_site"
    __table_args__ = (
        CheckConstraint(DELIVERY_MILESTONE_CHECK, name="ck_proc_dsite_milestone"),
        CheckConstraint(
            "status IN ('pending','in_progress','delivered','installed','on_hold','cancelled')",
            name="ck_proc_dsite_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_delivery_project.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    circle: Mapped[str | None] = mapped_column(String(120), nullable=True)
    site_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    site_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    customer_po_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ovf_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    order_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_order_header.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    item_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    milestone: Mapped[str] = mapped_column(
        String(40), nullable=False, default="order_placed", server_default="order_placed"
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending")
    expected_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    awb_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    delay_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    history: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
