"""Service visit ORM per ERD_16 section 6.9."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceVisit(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_visit"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_visit_doc"),
        CheckConstraint(
            "status IN ('planned','checked_in','completed','cancelled')",
            name="ck_svc_service_visit_status",
        ),
        {"schema": "service"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    work_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    technician_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    visit_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    visit_ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    site_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    geo_lat: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    customer_signoff_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
