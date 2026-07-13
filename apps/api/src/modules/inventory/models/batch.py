"""Inventory batch / lot ORM model."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.inventory.models.mixins import InvMasterMixin


class InvBatch(Base, *InvMasterMixin):
    __tablename__ = "inv_batch"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "product_id", "batch_number", name="uk_inv_batch_company_product_number"
        ),
        CheckConstraint(
            "status IN ('active','expired','quarantined','closed')",
            name="ck_inv_batch_status",
        ),
        CheckConstraint(
            "expiry_date IS NULL OR manufacturing_date IS NULL "
            "OR expiry_date >= manufacturing_date",
            name="ck_inv_batch_dates",
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
    product_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    batch_number: Mapped[str] = mapped_column(String(50), nullable=False)
    manufacturing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    barcode_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
