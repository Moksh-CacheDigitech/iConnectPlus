"""HR designation catalog ORM."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrMasterMixin


class HrDesignation(Base, *HrMasterMixin):
    __tablename__ = "hr_designation"
    __table_args__ = (
        UniqueConstraint("company_id", "designation_code", name="uk_hr_desig_company_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_hr_desig_status"),
        CheckConstraint(
            "job_level IS NULL OR job_level IN ('junior','mid','senior','lead','exec')",
            name="ck_hr_desig_job_level",
        ),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    designation_code: Mapped[str] = mapped_column(String(50), nullable=False)
    designation_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_level: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
