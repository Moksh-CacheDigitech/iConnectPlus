"""Service work order ORM per ERD_16 section 6.6."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceWorkOrder(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_work_order"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_work_order_doc"),
        CheckConstraint(
            "work_order_type IN ('preventive','corrective','breakdown','installation','other')",
            name="ck_svc_service_work_order_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','assigned','in_progress',"
            "'completed','closed','cancelled')",
            name="ck_svc_service_work_order_status",
        ),
        {"schema": "service"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_ticket.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    work_order_type: Mapped[str] = mapped_column(String(40), nullable=False)
    primary_technician_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    asset_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    maintenance_plan_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    inventory_issue_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    inventory_receipt_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    purchase_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    project_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    production_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    quality_inspection_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    estimated_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    actual_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

