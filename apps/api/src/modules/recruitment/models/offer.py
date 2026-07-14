"""Offer ORM per ERD_13 §6.10."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.recruitment.models.mixins import RecTransactionMixin


class RecOffer(Base, *RecTransactionMixin):
    __tablename__ = "rec_offer"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_rec_offer_company_doc"),
        CheckConstraint(
            "employment_type IN ('permanent','contract','intern','consultant')",
            name="ck_rec_offer_employment_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','sent','accepted','rejected','expired','withdrawn','cancelled')",
            name="ck_rec_offer_status",
        ),
        {"schema": "recruitment"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    application_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_application.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    candidate_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_candidate.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    job_requisition_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("recruitment.rec_job_requisition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    department_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_department.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    designation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    offered_ctc: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    offered_gross: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    offer_valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    employment_type: Mapped[str] = mapped_column(String(30), nullable=False)
    salary_structure_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    offer_letter_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)

    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="SET NULL"),
        nullable=True,
    )

