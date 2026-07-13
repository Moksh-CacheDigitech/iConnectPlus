"""Asset master ORM model."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.master_data.models.mixins import MasterBranchRecordMixin


class MasterAsset(Base, *MasterBranchRecordMixin):
    __tablename__ = "master_asset"
    __table_args__ = (
        UniqueConstraint("company_id", "asset_code", name="uk_master_asset_company_code"),
        CheckConstraint(
            "status IN ('draft','active','disposed','written_off')",
            name="ck_master_asset_status",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    asset_code: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_category: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    purchase_value: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    location_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_location.id", ondelete="RESTRICT"),
        nullable=True,
    )
    custodian_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    depreciation_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    useful_life_months: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    custodian: Mapped["MasterEmployee | None"] = relationship(foreign_keys=[custodian_employee_id])


from modules.master_data.models.employee import MasterEmployee  # noqa: E402
