"""HR employee document metadata ORM."""

from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.hr.models.mixins import HrTransactionMixin


class HrEmployeeDocument(Base, *HrTransactionMixin):
    __tablename__ = "hr_employee_document"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_hr_edoc_company_doc"),
        CheckConstraint(
            "document_type IN ('id_proof','address_proof','contract','certificate','other')",
            name="ck_hr_edoc_type",
        ),
        CheckConstraint(
            "verification_status IN ('pending','verified','rejected')",
            name="ck_hr_edoc_verification",
        ),
        CheckConstraint("status IN ('active','archived')", name="ck_hr_edoc_status"),
        {"schema": "hr"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(500), nullable=False)
    issued_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    verification_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
