"""Asset maintenance plan ORM per ERD_15 section 6.9."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetMaintenancePlan(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_maintenance_plan"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_maint_plan_doc"),
        CheckConstraint(
            "maintenance_type IN ('preventive','corrective','emergency','annual_service')",
            name="ck_ast_asset_maint_plan_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','paused','closed')",
            name="ck_ast_asset_maint_plan_status",
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

    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    plan_name: Mapped[str] = mapped_column(String(255), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(40), nullable=False)
    frequency_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frequency_meter_units: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
