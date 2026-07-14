"""Manufacturing work center ORM."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.manufacturing.models.mixins import MfgMasterMixin

if TYPE_CHECKING:
    from modules.manufacturing.models.machine import MfgMachine


class MfgWorkCenter(Base, *MfgMasterMixin):
    __tablename__ = "mfg_work_center"
    __table_args__ = (
        UniqueConstraint("company_id", "work_center_code", name="uk_mfg_wc_company_code"),
        CheckConstraint(
            "work_center_type IN ("
            "'machine','assembly_line','packaging_line','inspection_station')",
            name="ck_mfg_wc_type",
        ),
        CheckConstraint(
            "status IN ('active','inactive','maintenance')",
            name="ck_mfg_wc_status",
        ),
        {"schema": "manufacturing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    work_center_code: Mapped[str] = mapped_column(String(50), nullable=False)
    work_center_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_center_type: Mapped[str] = mapped_column(String(30), nullable=False, default="machine")
    capacity_per_shift: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    shift_count: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)

    machines: Mapped[list[MfgMachine]] = relationship(back_populates="work_center")
