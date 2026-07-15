"""Promotion ORM per ERD_22 section 5.17."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcPromotion(Base, *EcRowMixin):
    __tablename__ = "ec_promotion"
    __table_args__ = (
        UniqueConstraint("company_id", "promotion_number", name="uk_ec_promotion_number"),
        UniqueConstraint("company_id", "promotion_code", name="uk_ec_promotion_code"),
        CheckConstraint(
            "promotion_type IN ('percent','coupon_linked','bundle','flash_sale','seasonal')",
            name="ck_ec_promotion_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','paused','expired','cancelled')",
            name="ck_ec_promotion_status",
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

    promotion_number: Mapped[str] = mapped_column(String(50), nullable=False)

    store_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_store.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    promotion_code: Mapped[str] = mapped_column(String(50), nullable=False)
    promotion_name: Mapped[str] = mapped_column(String(255), nullable=False)
    promotion_type: Mapped[str] = mapped_column(String(40), nullable=False)
    channel_scope_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    rules_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    valid_from: Mapped[datetime | None] = mapped_column(nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
