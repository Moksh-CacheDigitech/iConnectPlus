"""Service assignment ORM per ERD_16 section 6.4."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceAssignment(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_assignment"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_assignment_doc"),
        CheckConstraint(
            "role_on_job IN ('primary','secondary','observer')",
            name="ck_svc_service_assignment_role",
        ),
        CheckConstraint(
            "status IN ('draft','active','completed','cancelled')",
            name="ck_svc_service_assignment_status",
        ),
        {"schema": "service"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    ticket_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_ticket.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_work_order.id",
            ondelete="RESTRICT",
            use_alter=True,
            name="fk_svc_assignment_work_order",
        ),
        nullable=True,
        index=True,
    )
    technician_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    role_on_job: Mapped[str] = mapped_column(String(30), nullable=False, default="primary")
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    unassigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
