"""Payment transaction ORM per ERD_22 section 5.11."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcPaymentTransaction(Base, *EcRowMixin):
    __tablename__ = "ec_payment_transaction"
    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('authorize','capture','refund','void','chargeback')",
            name="ck_ec_payment_transaction_type",
        ),
        CheckConstraint(
            "status IN ('recorded','posted','failed')",
            name="ck_ec_payment_transaction_status",
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


    payment_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_payment.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    gateway_txn_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    occurred_at: Mapped[datetime | None] = mapped_column(nullable=True)
    raw_payload_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
