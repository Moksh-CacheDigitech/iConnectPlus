"""Manufacturing production order ORM models."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.manufacturing.models.mixins import MfgTransactionMixin, MfgTxnLineMixin


class MfgProductionOrder(Base, *MfgTransactionMixin):
    __tablename__ = "mfg_production_order"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_mfg_wo_company_number"),
        CheckConstraint("planned_qty > 0", name="ck_mfg_wo_planned_qty"),
        CheckConstraint(
            "completed_qty >= 0 AND scrapped_qty >= 0",
            name="ck_mfg_wo_qty_nonneg",
        ),
        CheckConstraint(
            "status IN ("
            "'draft','released','in_progress','completed','closed','cancelled')",
            name="ck_mfg_wo_status",
        ),
        {"schema": "manufacturing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    bom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_bom.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    routing_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_routing.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    warehouse_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_warehouse.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    planned_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    completed_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    scrapped_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=False,
    )
    planned_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    cost_center_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_cost_center.id", ondelete="RESTRICT"),
        nullable=True,
    )
    source_module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_document_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    fiscal_year_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_fiscal_year.id", ondelete="RESTRICT"),
        nullable=True,
    )
    period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_period.id", ondelete="RESTRICT"),
        nullable=True,
    )

    operations: Mapped[list["MfgProductionOperation"]] = relationship(
        back_populates="production_order", cascade="all, delete-orphan"
    )


class MfgProductionOperation(Base, *MfgTxnLineMixin):
    __tablename__ = "mfg_production_operation"
    __table_args__ = (
        UniqueConstraint(
            "production_order_id", "operation_seq", name="uk_mfg_prod_op_order_seq"
        ),
        CheckConstraint(
            "planned_qty >= 0 AND produced_qty >= 0 AND rejected_qty >= 0",
            name="ck_mfg_prod_op_qty",
        ),
        CheckConstraint(
            "status IN ('pending','in_progress','completed','skipped')",
            name="ck_mfg_prod_op_status",
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
    operation_seq: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    routing_operation_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_routing_operation.id", ondelete="RESTRICT"),
        nullable=True,
    )
    work_center_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_work_center.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    machine_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_machine.id", ondelete="RESTRICT"),
        nullable=True,
    )
    operator_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
    )
    planned_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    produced_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    rejected_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    setup_time_actual: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    run_time_actual: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")

    production_order: Mapped[MfgProductionOrder] = relationship(back_populates="operations")
