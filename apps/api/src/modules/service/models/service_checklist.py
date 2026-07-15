"""Service checklist ORM per ERD_16 section 6.8."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceChecklist(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_checklist"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','completed','cancelled')",
            name="ck_svc_service_checklist_status",
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

    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    visit_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_visit.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_checklist_visit",
        ),
        nullable=True,
        index=True,
    )
    task_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_task.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    checklist_code: Mapped[str] = mapped_column(String(50), nullable=False)
    checklist_name: Mapped[str] = mapped_column(String(255), nullable=False)
    items_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
