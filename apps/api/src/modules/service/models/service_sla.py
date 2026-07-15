"""Service SLA ORM per ERD_16 section 6.13."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcDetailMixin


class SvcServiceSla(Base, *SvcDetailMixin):
    __tablename__ = "svc_service_sla"
    __table_args__ = (
        UniqueConstraint("company_id", "sla_code", name="uk_svc_service_sla_code"),
        CheckConstraint(
            "priority IN ('low','medium','high','critical')",
            name="ck_svc_service_sla_priority",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_svc_service_sla_status",
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

    sla_code: Mapped[str] = mapped_column(String(50), nullable=False)
    sla_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_contract.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_sla_contract",
        ),
        nullable=True,
        index=True,
    )
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    response_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    business_hours_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
