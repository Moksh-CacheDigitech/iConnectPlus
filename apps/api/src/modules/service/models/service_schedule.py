"""Service schedule ORM per ERD_16 section 6.5."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceSchedule(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_schedule"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_schedule_doc"),
        CheckConstraint(
            "status IN ('planned','confirmed','in_progress','completed','cancelled')",
            name="ck_svc_service_schedule_status",
        ),
        {"schema": "service"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_work_order.id",
            ondelete="RESTRICT",
            use_alter=True,
            name="fk_svc_schedule_work_order",
        ),
        nullable=False,
        index=True,
    )
    technician_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    planned_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    planned_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
