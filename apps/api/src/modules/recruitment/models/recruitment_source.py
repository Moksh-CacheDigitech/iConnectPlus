"""Recruitment source catalog ORM per ERD_13 §6.15."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecRecruitmentSource(Base, *RecMasterMixin):
    __tablename__ = "rec_recruitment_source"
    __table_args__ = (
        UniqueConstraint("company_id", "source_code", name="uk_rec_source_company_code"),
        CheckConstraint(
            "source_type IN ('organic','paid','agency','referral','campus','internal')",
            name="ck_rec_source_type",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_rec_source_status"),
        {"schema": "recruitment"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    source_code: Mapped[str] = mapped_column(String(50), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
