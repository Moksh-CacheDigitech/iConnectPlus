"""Service resolution ORM per ERD_16 section 6.16."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceResolution(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_resolution"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_resolution_doc"),
        CheckConstraint(
            "resolution_code IN ('fixed','workaround','duplicate','cannot_reproduce','other')",
            name="ck_svc_service_resolution_code",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','completed','cancelled')",
            name="ck_svc_service_resolution_status",
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
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_ticket.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    resolution_code: Mapped[str] = mapped_column(String(40), nullable=False)
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_time_fix: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

