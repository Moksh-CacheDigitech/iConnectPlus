"""Coupon ORM per ERD_22 section 5.16."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcCoupon(Base, *EcRowMixin):
    __tablename__ = "ec_coupon"
    __table_args__ = (
        UniqueConstraint("company_id", "coupon_number", name="uk_ec_coupon_number"),
        UniqueConstraint("company_id", "coupon_code", name="uk_ec_coupon_code"),
        CheckConstraint(
            "discount_type IN ('percent','fixed_amount','free_shipping')",
            name="ck_ec_coupon_discount_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','exhausted','expired','cancelled')",
            name="ck_ec_coupon_status",
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

    coupon_number: Mapped[str] = mapped_column(String(50), nullable=False)

    store_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_store.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    coupon_code: Mapped[str] = mapped_column(String(50), nullable=False)
    discount_type: Mapped[str] = mapped_column(String(30), nullable=False)
    discount_value: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    max_redemptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    redeemed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valid_from: Mapped[datetime | None] = mapped_column(nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
