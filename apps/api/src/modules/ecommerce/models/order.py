"""Channel order ORM per ERD_22 section 5.8."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcOrder(Base, *EcRowMixin):
    __tablename__ = "ec_order"
    __table_args__ = (
        UniqueConstraint("company_id", "order_number", name="uk_ec_order_number"),
        CheckConstraint(
            "status IN ('new','submitted','under_review','accepted','processing','packed',"
            "'shipped','delivered','returned','cancelled','failed')",
            name="ck_ec_order_status",
        ),
        Index("ix_ec_order_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "ecommerce"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    order_number: Mapped[str] = mapped_column(String(50), nullable=False)

    sales_channel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_sales_channel.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    store_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_store.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    cart_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_customer_cart.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    coupon_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    external_order_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    subtotal_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    shipping_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    grand_total: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    shipping_address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    billing_address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    sales_order_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    placed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="new", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
