"""Physical asset audit ORM per ERD_15 section 6.15."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstTransactionMixin


class AstAssetAudit(Base, *AstTransactionMixin):
    __tablename__ = "ast_asset_audit"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_audit_doc"),
        CheckConstraint(
            "found_status IN ('found','missing','damaged','relocated')",
            name="ck_ast_asset_audit_found",
        ),
        CheckConstraint(
            "status IN ('planned','in_progress','completed','cancelled')",
            name="ck_ast_asset_audit_status",
        ),
        {"schema": "asset"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("asset.ast_asset.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    audit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    auditor_employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    found_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned", index=True)
