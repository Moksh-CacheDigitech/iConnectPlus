"""Procurement vendor contract ORM models."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.procurement.models.mixins import ProcMasterMixin


class ProcVendorContract(Base, *ProcMasterMixin):
    __tablename__ = "proc_vendor_contract"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "document_number", name="uk_proc_vct_company_number"
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="ck_proc_vct_dates",
        ),
        CheckConstraint(
            "status IN ('draft','active','expired','terminated')",
            name="ck_proc_vct_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
    )
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    vendor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    contract_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    contract_value: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )

    lines: Mapped[list["ProcVendorContractLine"]] = relationship(
        back_populates="contract",
        cascade="all, delete-orphan",
    )


class ProcVendorContractLine(Base, *ProcMasterMixin):
    __tablename__ = "proc_vendor_contract_line"
    __table_args__ = (
        UniqueConstraint("contract_id", "line_number", name="uk_proc_vctl_contract_line"),
        CheckConstraint("unit_cost > 0", name="ck_proc_vctl_unit_cost"),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_proc_vctl_status",
        ),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
    )
    contract_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_vendor_contract.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    product_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=True,
    )
    min_quantity: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    max_quantity: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    unit_cost: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    contract: Mapped[ProcVendorContract] = relationship(back_populates="lines")
