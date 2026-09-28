"""Per-visit service rate contracts (freelancers / field partners) and their use on OVFs."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.procurement.models.mixins import ProcTransactionMixin


class ProcServiceRateContract(Base, *ProcTransactionMixin):
    __tablename__ = "proc_service_rate_contract"
    __table_args__ = (
        CheckConstraint("rate_per_visit > 0", name="ck_proc_src_rate"),
        CheckConstraint(
            "service_type IN ('site_visit','installation','survey','maintenance','manpower','other')",
            name="ck_proc_src_service_type",
        ),
        CheckConstraint("status IN ('active','inactive')", name="ck_proc_src_status"),
        CheckConstraint("valid_to IS NULL OR valid_to >= valid_from", name="ck_proc_src_validity"),
        UniqueConstraint("company_id", "contract_code", name="uk_proc_src_company_code"),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    contract_code: Mapped[str] = mapped_column(String(50), nullable=False)
    vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_type: Mapped[str] = mapped_column(String(30), nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    rate_per_visit: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProcServicePlan(Base, *ProcTransactionMixin):
    """Projected visits for one OVF priced off a rate contract."""

    __tablename__ = "proc_service_plan"
    __table_args__ = (
        CheckConstraint("projected_visits > 0", name="ck_proc_splan_visits"),
        CheckConstraint("consumables_amount >= 0", name="ck_proc_splan_consumables"),
        CheckConstraint("status IN ('open','closed')", name="ck_proc_splan_status"),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    # Soft link to crm.crm_ovf - no cross-module FK.
    ovf_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    rate_contract_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_service_rate_contract.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    projected_visits: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_per_visit: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    consumables_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, server_default="0")
    planned_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    visits_done: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    added_to_ovf: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", server_default="open")


class ProcServiceVisit(Base, *ProcTransactionMixin):
    __tablename__ = "proc_service_visit"
    __table_args__ = (
        CheckConstraint("status IN ('done','cancelled')", name="ck_proc_svisit_status"),
        {"schema": "procurement"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("procurement.proc_service_plan.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    site: Mapped[str | None] = mapped_column(String(255), nullable=True)
    engineer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="done", server_default="done")
    beyond_projection: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    # Soft link to crm.crm_ovf_expense raised for a visit beyond the projection.
    expense_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
