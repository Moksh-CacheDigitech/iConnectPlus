"""Service escalation ORM per ERD_16 section 6.14."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceEscalation(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_escalation"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_escalation_doc"),
        CheckConstraint(
            "reason_code IN ('sla_at_risk','sla_breached','customer_complaint','management')",
            name="ck_svc_service_escalation_reason",
        ),
        CheckConstraint(
            "status IN ('open','acknowledged','resolved','cancelled')",
            name="ck_svc_service_escalation_status",
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
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    sla_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_sla.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    escalation_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    reason_code: Mapped[str] = mapped_column(String(40), nullable=False)
    escalated_to_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

