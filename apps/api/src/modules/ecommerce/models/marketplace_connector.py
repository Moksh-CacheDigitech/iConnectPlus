"""Marketplace connector ORM per ERD_22 section 5.18."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcMarketplaceConnector(Base, *EcRowMixin):
    __tablename__ = "ec_marketplace_connector"
    __table_args__ = (
        UniqueConstraint("company_id", "connector_binding_number", name="uk_ec_marketplace_connector_number"),
        CheckConstraint(
            "marketplace_code IN ('amazon','flipkart','myntra','ebay','etsy','shopify','custom')",
            name="ck_ec_marketplace_connector_code",
        ),
        CheckConstraint(
            "sync_mode IN ('realtime','scheduled','manual')",
            name="ck_ec_marketplace_connector_sync_mode",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','active','paused','failed','retired')",
            name="ck_ec_marketplace_connector_status",
        ),
        Index("ix_ec_marketplace_connector_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "ecommerce"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    connector_binding_number: Mapped[str] = mapped_column(String(50), nullable=False)

    sales_channel_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_sales_channel.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    marketplace_code: Mapped[str] = mapped_column(String(40), nullable=False)

    int_external_system_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    int_connector_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    sync_mode: Mapped[str] = mapped_column(String(30), nullable=False, default="scheduled")
    last_sync_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
