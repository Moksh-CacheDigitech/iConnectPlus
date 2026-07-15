"""Asset service history ORM per ERD_15 section 6.11."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetServiceHistory(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_service_history"
    __table_args__ = (
        CheckConstraint(
            "status IN ('recorded')",
            name="ck_ast_asset_service_history_status",
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
    maintenance_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_maintenance.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    service_summary: Mapped[str] = mapped_column(Text, nullable=False)
    parts_replaced_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    serviced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="recorded", index=True)
