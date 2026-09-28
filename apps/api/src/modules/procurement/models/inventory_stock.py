"""Procurement stock on hand - one row per unit added from GRN receipt (not billed portion)."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.procurement.models.mixins import ProcTransactionMixin


class ProcInventoryStockUnit(Base, *ProcTransactionMixin):
    __tablename__ = "proc_inventory_stock_unit"
    __table_args__ = {"schema": "procurement"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    order_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_order_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_line_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_order_line.id", ondelete="RESTRICT"),
        nullable=False,
    )
    receipt_batch_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_order_receipt_batch.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    grn_number: Mapped[str] = mapped_column(String(80), nullable=False)
    receipt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    unit_index: Mapped[int] = mapped_column(Integer, nullable=False)
    serial_number: Mapped[str] = mapped_column(String(120), nullable=False)
    # 1 for whole units; fractional for partial unbilled GRN stock.
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    warranty_valid_till: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Salesperson accountable for the unit (the OVF owner who ordered it).
    owner_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    owner_assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Soft link to crm.crm_ovf - no cross-module FK.
    source_ovf_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    open_for_sale: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    open_for_sale_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
