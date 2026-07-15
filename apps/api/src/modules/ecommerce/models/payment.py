"""Payment ORM per ERD_22 section 5.10."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcPayment(Base, *EcRowMixin):
    __tablename__ = "ec_payment"
    __table_args__ = (
        UniqueConstraint("company_id", "payment_number", name="uk_ec_payment_number"),
        CheckConstraint(
            "payment_method IN ('card','upi','netbanking','wallet','cod','marketplace_collect','other')",
            name="ck_ec_payment_method",
        ),
        CheckConstraint(
            "status IN ('pending','authorized','captured','failed','refunded','cancelled')",
            name="ck_ec_payment_status",
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

    payment_number: Mapped[str] = mapped_column(String(50), nullable=False)

    order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_order.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    gateway_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gateway_payment_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(nullable=True)

    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", index=True)
