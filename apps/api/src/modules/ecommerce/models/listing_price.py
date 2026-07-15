"""Listing price ORM per ERD_22 section 5.4."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcListingPrice(Base, *EcRowMixin):
    __tablename__ = "ec_listing_price"
    __table_args__ = (
        CheckConstraint(
            "price_type IN ('retail','wholesale','contract','promotional')",
            name="ck_ec_listing_price_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','expired','superseded')",
            name="ck_ec_listing_price_status",
        ),
        {"schema": "ecommerce"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )


    product_listing_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_product_listing.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    price_type: Mapped[str] = mapped_column(String(30), nullable=False, default="retail")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    list_price: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    sale_price: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    effective_from: Mapped[datetime | None] = mapped_column(nullable=True)
    effective_to: Mapped[datetime | None] = mapped_column(nullable=True)

    promotion_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
