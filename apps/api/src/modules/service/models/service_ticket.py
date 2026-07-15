"""Service ticket ORM per ERD_16 section 6.3."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceTicket(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_ticket"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_ticket_doc"),
        CheckConstraint(
            "ticket_type IN ('incident','request','problem','change')",
            name="ck_svc_service_ticket_type",
        ),
        CheckConstraint(
            "status IN ('open','pending','in_progress','resolved','closed','cancelled')",
            name="ck_svc_service_ticket_status",
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
    ticket_type: Mapped[str] = mapped_column(String(40), nullable=False, default="incident")
    queue_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
