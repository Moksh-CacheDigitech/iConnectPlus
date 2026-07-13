"""Cost center allocation ORM model."""

from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.finance.models.mixins import FinanceTransactionMixin


class FinCostCenterAllocation(Base, *FinanceTransactionMixin):
    __tablename__ = "fin_cost_center_allocation"
    __table_args__ = (
        UniqueConstraint(
            "journal_line_id",
            "allocation_sequence",
            name="uk_fin_cost_center_allocation_line_seq",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    journal_line_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_line.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    gl_entry_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_gl_entry.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    cost_center_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_cost_center.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    allocation_sequence: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    allocation_percent: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    allocated_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
