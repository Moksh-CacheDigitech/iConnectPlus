"""Manufacturing production variance ORM model."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.manufacturing.models.mixins import MfgTransactionMixin


class MfgVariance(Base, *MfgTransactionMixin):
    __tablename__ = "mfg_variance"
    __table_args__ = (
        CheckConstraint(
            "variance_type IN ('material','labor','overhead','quantity')",
            name="ck_mfg_var_type",
        ),
        CheckConstraint(
            "status IN ('open','posted')",
            name="ck_mfg_var_status",
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
    variance_type: Mapped[str] = mapped_column(String(30), nullable=False)
    standard_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    actual_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    variance_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
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
