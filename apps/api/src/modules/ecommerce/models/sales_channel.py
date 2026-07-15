"""Sales channel ORM per ERD_22 section 5.2."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcSalesChannel(Base, *EcRowMixin):
    __tablename__ = "ec_sales_channel"
    __table_args__ = (
        UniqueConstraint("company_id", "channel_number", name="uk_ec_sales_channel_number"),
        UniqueConstraint("company_id", "channel_code", name="uk_ec_sales_channel_code"),
        CheckConstraint(
            "channel_type IN ('website','mobile_app','amazon','flipkart','shopify',"
            "'woocommerce','magento','ebay','etsy','custom_marketplace','dealer_portal',"
            "'distributor_portal')",
            name="ck_ec_sales_channel_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','paused','retired')",
            name="ck_ec_sales_channel_status",
        ),
        Index("ix_ec_sales_channel_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "ecommerce"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    channel_number: Mapped[str] = mapped_column(String(50), nullable=False)
    channel_code: Mapped[str] = mapped_column(String(50), nullable=False)
    channel_name: Mapped[str] = mapped_column(String(255), nullable=False)

    store_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_store.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    channel_type: Mapped[str] = mapped_column(String(40), nullable=False)
    external_channel_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
