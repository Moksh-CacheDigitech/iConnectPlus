"""GST registrations of a CRM sales account (one account, many GSTINs / branches)."""

from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.crm.models.mixins import CrmTransactionMixin


class CrmCompanyGst(Base, *CrmTransactionMixin):
    __tablename__ = "crm_company_gst"
    __table_args__ = (
        CheckConstraint("source IN ('manual','customer_po','kyc')", name="ck_crm_company_gst_source"),
        CheckConstraint("status IN ('active','inactive')", name="ck_crm_company_gst_status"),
        Index(
            "uq_crm_company_gst_account_gstin",
            "company_account_id",
            "gstin",
            unique=True,
            postgresql_where=text("is_deleted = false"),
        ),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("crm.crm_company.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    gstin: Mapped[str] = mapped_column(String(15), nullable=False)
    state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    billing_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_head_office: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    certificate_attachment_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual", server_default="manual")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
