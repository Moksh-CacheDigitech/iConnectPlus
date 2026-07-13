"""Warehouse master ORM model."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.master_data.models.mixins import MasterBranchRecordMixin


class MasterWarehouse(Base, *MasterBranchRecordMixin):
    __tablename__ = "master_warehouse"
    __table_args__ = (
        UniqueConstraint("company_id", "warehouse_code", name="uk_master_warehouse_company_code"),
        CheckConstraint(
            "warehouse_type IN ('central','transit','retail','quarantine')",
            name="ck_master_warehouse_type",
        ),
        CheckConstraint(
            "status IN ('active','inactive')",
            name="ck_master_warehouse_status",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    warehouse_code: Mapped[str] = mapped_column(String(50), nullable=False)
    warehouse_name: Mapped[str] = mapped_column(String(255), nullable=False)
    warehouse_type: Mapped[str] = mapped_column(String(30), nullable=False)
    location_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_location.id", ondelete="RESTRICT"),
        nullable=True,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
