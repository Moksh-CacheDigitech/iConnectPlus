"""Salesperson request to take over stock held by another owner."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.procurement.models.mixins import ProcTransactionMixin


class ProcInventoryTransferRequest(Base, *ProcTransactionMixin):
    __tablename__ = "proc_inventory_transfer_request"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_proc_inv_transfer_qty"),
        CheckConstraint(
            "status IN ('pending','accepted','rejected','cancelled')",
            name="ck_proc_inv_transfer_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    requester_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    stock_unit_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    import_line_ids: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    customer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending")
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    decision_remark: Mapped[str | None] = mapped_column(Text, nullable=True)
