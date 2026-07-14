"""Manufacturing material issue ORM models."""

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


class MfgMaterialIssue(Base, *MfgTransactionMixin):
    __tablename__ = "mfg_material_issue"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_mfg_mi_company_number"),
        CheckConstraint(
            "status IN ('draft','confirmed','cancelled')",
            name="ck_mfg_mi_status",
        ),
        {"schema": "manufacturing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    production_order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_production_order.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_warehouse.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    issued_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    period_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_period.id", ondelete="RESTRICT"),
        nullable=True,
    )

    lines: Mapped[list["MfgMaterialIssueLine"]] = relationship(
        back_populates="material_issue", cascade="all, delete-orphan"
    )


class MfgMaterialIssueLine(Base, *MfgTxnLineMixin):
    __tablename__ = "mfg_material_issue_line"
    __table_args__ = (
        UniqueConstraint("material_issue_id", "line_number", name="uk_mfg_mi_line"),
        CheckConstraint("quantity > 0", name="ck_mfg_mi_line_qty"),
        {"schema": "manufacturing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    material_issue_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_material_issue.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    component_product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    uom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=False,
    )
    bom_line_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_bom_line.id", ondelete="RESTRICT"),
        nullable=True,
    )
    batch_reference: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    bin_reference: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    inventory_event_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")

    material_issue: Mapped[MfgMaterialIssue] = relationship(back_populates="lines")
