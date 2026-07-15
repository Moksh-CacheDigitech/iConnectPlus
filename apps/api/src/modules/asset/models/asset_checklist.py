"""Asset checklist ORM per ERD_15 section 6.17."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetChecklist(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_checklist"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','completed','cancelled')",
            name="ck_ast_asset_checklist_status",
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

    asset_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    maintenance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_maintenance.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    audit_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset_audit.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    checklist_code: Mapped[str] = mapped_column(String(50), nullable=False)
    checklist_name: Mapped[str] = mapped_column(String(255), nullable=False)
    items_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
