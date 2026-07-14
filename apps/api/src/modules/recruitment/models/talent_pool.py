"""Talent pool membership ORM per ERD_13 §6.16."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecTalentPool(Base, *RecMasterMixin):
    __tablename__ = "rec_talent_pool"
    __table_args__ = (
        UniqueConstraint("company_id", "pool_code", "candidate_id", name="uk_rec_talent_pool_membership"),
        CheckConstraint(
            "availability IN ('passive','active','do_not_contact')",
            name="ck_rec_talent_pool_availability",
        ),
        CheckConstraint(
            "status IN ('active','removed','hired_out')",
            name="ck_rec_talent_pool_status",
        ),
        {"schema": "recruitment"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    pool_code: Mapped[str] = mapped_column(String(50), nullable=False)
    pool_name: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    skill_tags_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    availability: Mapped[str] = mapped_column(String(30), nullable=False, default="passive")
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
