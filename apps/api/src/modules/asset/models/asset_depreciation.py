"""Asset depreciation ORM per ERD_15 section 6.12."""

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.asset.models.mixins import AstDetailMixin


class AstAssetDepreciation(Base, *AstDetailMixin):
    __tablename__ = "ast_asset_depreciation"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_ast_asset_depreciation_doc"),
        UniqueConstraint(
            "asset_id", "period_year", "period_month", "idempotency_key",
            name="uk_ast_asset_depreciation_period",
        ),
        CheckConstraint(
            "method IN ('straight_line','wdv','units_of_production')",
            name="ck_ast_asset_depreciation_method",
        ),
        CheckConstraint(
            "status IN ('draft','calculated','posted','failed','reversed')",
            name="ck_ast_asset_depreciation_status",
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
    period_year: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    period_month: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(40), nullable=False)
    depreciation_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    book_value_after: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    units_produced: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    depreciation_batch_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
