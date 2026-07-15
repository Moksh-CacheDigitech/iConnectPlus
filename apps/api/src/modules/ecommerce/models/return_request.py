"""Return request ORM per ERD_22 section 5.14."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcReturnRequest(Base, *EcRowMixin):
    __tablename__ = "ec_return_request"
    __table_args__ = (
        UniqueConstraint("company_id", "return_number", name="uk_ec_return_request_number"),
        CheckConstraint(
            "reason_code IN ('defective','wrong_item','not_as_described','size_fit','changed_mind','other')",
            name="ck_ec_return_request_reason",
        ),
        CheckConstraint(
            "status IN ('requested','submitted','approved','rejected','pickup_scheduled',"
            "'received','inspected','refunded','closed','cancelled')",
            name="ck_ec_return_request_status",
        ),
        Index("ix_ec_return_request_tenant_co_status", "tenant_id", "company_id", "status"),
        {"schema": "ecommerce"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    return_number: Mapped[str] = mapped_column(String(50), nullable=False)

    order_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_order.id",
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
    reason_code: Mapped[str] = mapped_column(String(40), nullable=False)
    requested_at: Mapped[datetime | None] = mapped_column(nullable=True)

    refund_payment_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_payment.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    sales_return_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="requested", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )
