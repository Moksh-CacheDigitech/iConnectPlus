"""Inventory reorder policy ORM model."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.inventory.models.mixins import InvMasterMixin


class InvReorderPolicy(Base, *InvMasterMixin):
    __tablename__ = "inv_reorder_policy"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "warehouse_id",
            "product_id",
            name="uk_inv_rp_company_wh_product",
        ),
        CheckConstraint("reorder_point >= 0", name="ck_inv_rp_point"),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_inv_rp_status",
        ),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    warehouse_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_warehouse.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    reorder_point: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    safety_stock: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    reorder_qty: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
