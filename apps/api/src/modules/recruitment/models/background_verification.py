"""Background verification ORM per ERD_13 §6.12."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecBackgroundVerification(Base, *RecTransactionMixin):
    __tablename__ = "rec_background_verification"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_bgv_company_doc"),
        CheckConstraint(
            "result IN ('pending','clear','adverse','inconclusive')",
            name="ck_rec_bgv_result",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','in_progress','cleared','failed','waived','cancelled')",
            name="ck_rec_bgv_status",
        ),
        {"schema": "recruitment"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    offer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_offer.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    application_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    vendor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    verification_scope_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    initiated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    report_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

