"""Service category ORM per ERD_16 section 6.1."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcMasterMixin


class SvcServiceCategory(Base, *SvcMasterMixin):
    __tablename__ = "svc_service_category"
    __table_args__ = (
        UniqueConstraint("company_id", "category_code", name="uk_svc_service_category_code"),
        CheckConstraint(
            "default_priority IN ('low','medium','high','critical')",
            name="ck_svc_service_category_priority",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_svc_service_category_status",
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

    category_code: Mapped[str] = mapped_column(String(50), nullable=False)
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    default_sla_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "service.svc_service_sla.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_svc_category_default_sla",
        ),
        nullable=True,
        index=True,
    )
    is_billable_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
