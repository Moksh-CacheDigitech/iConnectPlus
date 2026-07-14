"""HR holiday calendar ORM."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrMasterMixin


class HrHolidayCalendar(Base, *HrMasterMixin):
    __tablename__ = "hr_holiday_calendar"
    __table_args__ = (
        UniqueConstraint("company_id", "calendar_code", name="uk_hr_hol_company_code"),
        CheckConstraint(
            "status IN ('draft','published','archived')",
            name="ck_hr_hol_status",
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
    calendar_code: Mapped[str] = mapped_column(String(50), nullable=False)
    calendar_name: Mapped[str] = mapped_column(String(255), nullable=False)
    calendar_year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    holidays_json: Mapped[list | dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
