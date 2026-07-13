"""Inventory bin location ORM model."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.inventory.models.mixins import InvMasterMixin


class InvBin(Base, *InvMasterMixin):
    __tablename__ = "inv_bin"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "bin_code", name="uk_inv_bin_warehouse_code"),
        CheckConstraint(
            "bin_type IN ('storage','quarantine','staging','in_transit')",
            name="ck_inv_bin_type",
        ),
        CheckConstraint(
            "status IN ('active','inactive','blocked')",
            name="ck_inv_bin_status",
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
    bin_code: Mapped[str] = mapped_column(String(50), nullable=False)
    bin_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    aisle: Mapped[str | None] = mapped_column(String(30), nullable=True)
    rack: Mapped[str | None] = mapped_column(String(30), nullable=True)
    shelf: Mapped[str | None] = mapped_column(String(30), nullable=True)
    parent_bin_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("inventory.inv_bin.id", ondelete="RESTRICT"),
        nullable=True,
    )
    bin_type: Mapped[str] = mapped_column(String(30), nullable=False, default="storage")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
