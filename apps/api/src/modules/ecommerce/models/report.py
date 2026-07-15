"""Report ORM per ERD_22 section 5.20."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.ecommerce.models.mixins import EcRowMixin


class EcReport(Base, *EcRowMixin):
    __tablename__ = "ec_report"
    __table_args__ = (
        UniqueConstraint("company_id", "report_code", name="uk_ec_report_code"),
        CheckConstraint(
            "report_type IN ('channel_revenue','orders','conversion','returns',"
            "'listing_sync','inventory_sync','promotion_performance')",
            name="ck_ec_report_type",
        ),
        CheckConstraint(
            "status IN ('draft','finalized')",
            name="ck_ec_report_status",
        ),
        {"schema": "ecommerce"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    branch_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_branch.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    report_code: Mapped[str] = mapped_column(String(50), nullable=False)

    store_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_store.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    sales_channel_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(
            "ecommerce.ec_sales_channel.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    metrics_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
