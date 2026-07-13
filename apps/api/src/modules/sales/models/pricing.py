"""Pricing ORM models: price lists, items, discount rules."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
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
from modules.sales.models.mixins import SalesMasterMixin


class SalesPriceList(Base, *SalesMasterMixin):
    __tablename__ = "sales_price_list"
    __table_args__ = (
        UniqueConstraint("company_id", "price_list_code", name="uk_sales_pl_company_code"),
        CheckConstraint(
            "price_list_type IN "
            "('standard','customer','volume','promotional','contract')",
            name="ck_sales_pl_type",
        ),
        CheckConstraint(
            "effective_to IS NULL OR effective_to >= effective_from",
            name="ck_sales_pl_dates",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive','expired')",
            name="ck_sales_pl_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    price_list_code: Mapped[str] = mapped_column(String(50), nullable=False)
    price_list_name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_list_type: Mapped[str] = mapped_column(String(30), nullable=False, default="standard")
    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=100)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    items: Mapped[list["SalesPriceListItem"]] = relationship(back_populates="price_list")


class SalesPriceListItem(Base, *SalesMasterMixin):
    __tablename__ = "sales_price_list_item"
    __table_args__ = (
        UniqueConstraint(
            "price_list_id",
            "product_id",
            "min_quantity",
            name="uk_sales_pli_list_product_qty",
        ),
        CheckConstraint("unit_price >= 0", name="ck_sales_pli_price"),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_sales_pli_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    price_list_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_price_list.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    product_code: Mapped[str] = mapped_column(String(50), nullable=False)
    min_quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    uom_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_uom.id", ondelete="RESTRICT"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")

    price_list: Mapped[SalesPriceList] = relationship(back_populates="items")


class SalesDiscountRule(Base, *SalesMasterMixin):
    __tablename__ = "sales_discount_rule"
    __table_args__ = (
        UniqueConstraint("company_id", "discount_code", name="uk_sales_dr_company_code"),
        CheckConstraint(
            "discount_type IN ('percent','fixed_amount','buy_x_get_y')",
            name="ck_sales_dr_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive')",
            name="ck_sales_dr_status",
        ),
        {"schema": "sales"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    discount_code: Mapped[str] = mapped_column(String(50), nullable=False)
    discount_name: Mapped[str] = mapped_column(String(255), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(30), nullable=False)
    discount_value: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    max_discount_percent: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=True,
    )
    product_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=True,
    )
    price_list_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sales.sales_price_list.id", ondelete="RESTRICT"),
        nullable=True,
    )
    min_order_amount: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
    )
