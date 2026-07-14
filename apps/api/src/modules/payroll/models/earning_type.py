"""Payroll earning type catalog ORM."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.payroll.models.mixins import PayMasterMixin


class PayEarningType(Base, *PayMasterMixin):
    __tablename__ = "pay_earning_type"
    __table_args__ = (
        UniqueConstraint("company_id", "earning_type_code", name="uk_pay_earn_type_code"),
        CheckConstraint("status IN ('active','inactive')", name="ck_pay_earn_type_status"),
        {"schema": "payroll"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    earning_type_code: Mapped[str] = mapped_column(String(50), nullable=False)
    earning_type_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
