"""Recruiter staff ORM per ERD_13 §6.14."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecMasterMixin


class RecRecruiter(Base, *RecMasterMixin):
    __tablename__ = "rec_recruiter"
    __table_args__ = (
        UniqueConstraint("company_id", "recruiter_code", name="uk_rec_recruiter_company_code"),
        UniqueConstraint("company_id", "employee_id", name="uk_rec_recruiter_company_employee"),
        CheckConstraint("status IN ('active','inactive')", name="ck_rec_recruiter_status"),
        {"schema": "recruitment"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    recruiter_code: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    max_open_requisitions: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
