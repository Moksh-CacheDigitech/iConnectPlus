"""HR shift catalog ORM."""

from datetime import time
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrMasterMixin


class HrShift(Base, *HrMasterMixin):
    __tablename__ = "hr_shift"
    __table_args__ = (
        UniqueConstraint("company_id", "shift_code", name="uk_hr_shift_company_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_hr_shift_status"),
        CheckConstraint(
            "shift_type IN ('general','morning','evening','night','rotational')",
            name="ck_hr_shift_type",
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
    shift_code: Mapped[str] = mapped_column(String(50), nullable=False)
    shift_name: Mapped[str] = mapped_column(String(255), nullable=False)
    shift_type: Mapped[str] = mapped_column(String(30), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    grace_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    break_minutes: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    is_overnight: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
