"""Customer and vendor master ORM models."""

from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.master_data.models.mixins import MasterBranchRecordMixin


class MasterCustomer(Base, *MasterBranchRecordMixin):
    __tablename__ = "master_customer"
    __table_args__ = (
        UniqueConstraint("company_id", "customer_code", name="uk_master_customer_company_code"),
        CheckConstraint(
            "customer_type IN ('individual','corporate','government')",
            name="ck_master_customer_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive','blocked')",
            name="ck_master_customer_status",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_code: Mapped[str] = mapped_column(String(50), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    customer_type: Mapped[str] = mapped_column(String(30), nullable=False)
    tax_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(30), nullable=True)
    billing_address_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    shipping_address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    credit_limit: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    currency_code: Mapped[str | None] = mapped_column(String(3), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)


class MasterVendor(Base, *MasterBranchRecordMixin):
    __tablename__ = "master_vendor"
    __table_args__ = (
        UniqueConstraint("company_id", "vendor_code", name="uk_master_vendor_company_code"),
        CheckConstraint(
            "vendor_type IN ('domestic','international','service')",
            name="ck_master_vendor_type",
        ),
        CheckConstraint(
            "status IN ('draft','active','inactive','blocked')",
            name="ck_master_vendor_status",
        ),
        {"schema": "master"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_code: Mapped[str] = mapped_column(String(50), nullable=False)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_type: Mapped[str] = mapped_column(String(30), nullable=False)
    tax_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(30), nullable=True)
    payment_terms: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bank_details_encrypted: Mapped[str | None] = mapped_column(String, nullable=True)
    address_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
