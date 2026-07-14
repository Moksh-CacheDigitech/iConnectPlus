"""Manufacturing routing ORM models."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
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


class MfgRouting(Base, *MfgMasterMixin):
    __tablename__ = "mfg_routing"
    __table_args__ = (
        UniqueConstraint("company_id", "routing_code", name="uk_mfg_routing_company_code"),
        CheckConstraint(
            "status IN ('draft','active','obsolete')",
            name="ck_mfg_routing_status",
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
    routing_code: Mapped[str] = mapped_column(String(50), nullable=False)
    routing_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    product_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    operations: Mapped[list["MfgRoutingOperation"]] = relationship(
        back_populates="routing", cascade="all, delete-orphan"
    )


class MfgRoutingOperation(Base, *MfgLineMixin):
    __tablename__ = "mfg_routing_operation"
    __table_args__ = (
        UniqueConstraint("routing_id", "operation_seq", name="uk_mfg_rtg_op_routing_seq"),
        CheckConstraint(
            "setup_time_minutes >= 0 AND run_time_minutes >= 0",
            name="ck_mfg_rtg_op_times",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_mfg_rtg_op_status"),
        {"schema": "manufacturing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
    )
    routing_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_routing.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    operation_seq: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    operation_code: Mapped[str] = mapped_column(String(50), nullable=False)
    operation_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    work_center_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("manufacturing.mfg_work_center.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    setup_time_minutes: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    run_time_minutes: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    routing: Mapped[MfgRouting] = relationship(back_populates="operations")
