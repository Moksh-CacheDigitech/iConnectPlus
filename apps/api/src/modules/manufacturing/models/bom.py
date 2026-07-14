"""Manufacturing BOM ORM models."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.manufacturing.models.mixins import MfgLineMixin, MfgMasterMixin


class MfgBom(Base, *MfgMasterMixin):
    __tablename__ = "mfg_bom"
    __table_args__ = (
        UniqueConstraint("company_id", "bom_number", name="uk_mfg_bom_company_number"),
        CheckConstraint(
            "status IN ('draft','active','obsolete')",
            name="ck_mfg_bom_status",
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
    bom_number: Mapped[str] = mapped_column(String(50), nullable=False)
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    revision: Mapped[str] = mapped_column(String(30), nullable=False, default="A")
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    lines: Mapped[list["MfgBomLine"]] = relationship(
        back_populates="bom", cascade="all, delete-orphan"
    )


class MfgBomLine(Base, *MfgLineMixin):
    __tablename__ = "mfg_bom_line"
    __table_args__ = (
        UniqueConstraint("bom_id", "line_number", name="uk_mfg_bom_line_bom_line"),
        CheckConstraint("quantity > 0", name="ck_mfg_bom_line_qty"),
        CheckConstraint(
            "scrap_percent >= 0 AND scrap_percent <= 100",
            name="ck_mfg_bom_line_scrap",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_mfg_bom_line_status"),
        {"schema": "manufacturing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
    )
    bom_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_bom.id", ondelete="RESTRICT"),
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
    scrap_percent: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False, default=0)
    alternate_product_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=True,
    )
    is_optional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    bom: Mapped[MfgBom] = relationship(back_populates="lines")
