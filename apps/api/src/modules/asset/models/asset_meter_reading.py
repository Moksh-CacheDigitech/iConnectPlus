"""Asset meter reading ORM per ERD_15 section 6.18."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetMeterReading(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_meter_reading"
    __table_args__ = (
        CheckConstraint(
            "meter_type IN ('odometer','runtime_hours','cycle_count','other')",
            name="ck_ast_asset_meter_type",
        ),
        CheckConstraint(
            "status IN ('recorded','void')",
            name="ck_ast_asset_meter_status",
        ),
        {"schema": "asset"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    meter_type: Mapped[str] = mapped_column(String(40), nullable=False)
    reading_value: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    reading_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_by_employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
