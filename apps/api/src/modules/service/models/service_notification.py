"""Service notification ORM per ERD_16 section 6.18."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceNotification(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_notification"
    __table_args__ = (
        CheckConstraint(
            "delivery_status IN ('pending','sent','failed','read')",
            name="ck_svc_service_notification_delivery",
        ),
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_svc_service_notification_status",
        ),
        {"schema": "service"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    contract_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_contract.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_notification_contract",
        ),
        nullable=True,
        index=True,
    )
    notification_type: Mapped[str] = mapped_column(String(60), nullable=False)
    recipient_user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    recipient_employee_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    recipient_customer_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
