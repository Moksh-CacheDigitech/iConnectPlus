"""Reference master ORM models: UOM, Currency, Tax."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.master_data.models.mixins import MasterCompanyRecordMixin


class MasterUom(Base, *MasterCompanyRecordMixin):
    __tablename__ = "master_uom"
    __table_args__ = (
        UniqueConstraint("company_id", "uom_code", name="uk_master_uom_company_code"),
        CheckConstraint(
            "uom_type IN ('weight','volume','count','length')",
            name="ck_master_uom_type",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_master_uom_status",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    uom_code: Mapped[str] = mapped_column(String(20), nullable=False)
    uom_name: Mapped[str] = mapped_column(String(100), nullable=False)
    uom_type: Mapped[str] = mapped_column(String(30), nullable=False)
    decimal_places: Mapped[int] = mapped_column(SmallInteger, default=2, server_default="2")
    is_base_uom: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")


class MasterCurrency(Base, *MasterCompanyRecordMixin):
    __tablename__ = "master_currency"
    __table_args__ = (
        UniqueConstraint("company_id", "currency_code", name="uk_master_currency_company_code"),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_master_currency_status",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    currency_name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(10), nullable=True)
    decimal_places: Mapped[int] = mapped_column(SmallInteger, default=2, server_default="2")
    is_base_currency: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    exchange_rate: Mapped[float | None] = mapped_column(Numeric(18, 8), nullable=True)
    rate_effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")


class MasterTax(Base, *MasterCompanyRecordMixin):
    __tablename__ = "master_tax"
    __table_args__ = (
        UniqueConstraint("company_id", "tax_code", name="uk_master_tax_company_code"),
        CheckConstraint(
            "tax_type IN ('gst','vat','sales_tax','withholding')",
            name="ck_master_tax_type",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_master_tax_status",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_master_tax_dates",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    tax_code: Mapped[str] = mapped_column(String(50), nullable=False)
    tax_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_type: Mapped[str] = mapped_column(String(30), nullable=False)
    rate_percent: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    is_compound: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
