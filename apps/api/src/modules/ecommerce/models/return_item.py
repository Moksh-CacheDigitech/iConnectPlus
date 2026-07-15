"""Return item ORM per ERD_22 section 5.15."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcReturnItem(Base, *EcRowMixin):
    __tablename__ = "ec_return_item"
    __table_args__ = (
        CheckConstraint(
            "condition_code IN ('sellable','damaged','missing_parts','other')",
            name="ck_ec_return_item_condition",
        ),
        CheckConstraint(
            "status IN ('open','approved','received','refunded','rejected')",
            name="ck_ec_return_item_status",
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


    return_request_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_return_request.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    order_item_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_order_item.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "master.master_product.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    quantity: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    condition_code: Mapped[str] = mapped_column(String(40), nullable=False, default="other")
    refund_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
