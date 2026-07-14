"""Manufacturing WIP ORM model."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.manufacturing.models.mixins import MfgTransactionMixin


class MfgWip(Base, *MfgTransactionMixin):
    __tablename__ = "mfg_wip"
    __table_args__ = (
        UniqueConstraint("production_order_id", name="uk_mfg_wip_production_order"),
        CheckConstraint(
            "material_cost >= 0 AND labor_cost >= 0 AND overhead_cost >= 0 AND total_cost >= 0",
            name="ck_mfg_wip_costs",
        ),
        CheckConstraint(
            "status IN ('open','relieved','closed')",
            name="ck_mfg_wip_status",
        ),
        {"schema": "manufacturing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    production_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_production_order.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    material_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
    period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_period.id", ondelete="RESTRICT"),
        nullable=True,
    )
    finance_journal_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
