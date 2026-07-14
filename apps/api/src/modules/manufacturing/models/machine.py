"""Manufacturing machine ORM."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.manufacturing.models.mixins import MfgMasterMixin

if TYPE_CHECKING:
    from modules.manufacturing.models.work_center import MfgWorkCenter


class MfgMachine(Base, *MfgMasterMixin):
    __tablename__ = "mfg_machine"
    __table_args__ = (
        UniqueConstraint("company_id", "machine_code", name="uk_mfg_machine_company_code"),
        CheckConstraint(
            "status IN ('idle','running','maintenance','breakdown')",
            name="ck_mfg_machine_status",
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
    machine_code: Mapped[str] = mapped_column(String(50), nullable=False)
    machine_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_center_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_work_center.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="idle", index=True)
    last_status_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    work_center: Mapped[MfgWorkCenter] = relationship(back_populates="machines")
