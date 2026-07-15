"""Service expense ORM per ERD_16 section 6.12."""

from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.service.models.mixins import SvcTransactionMixin


class SvcServiceExpense(Base, *SvcTransactionMixin):
    __tablename__ = "svc_service_expense"
    __table_args__ = (
        UniqueConstraint("company_id", "document_number", name="uk_svc_service_expense_doc"),
        CheckConstraint(
            "expense_type IN ('travel','lodging','meal','other','material_surcharge')",
            name="ck_svc_service_expense_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','posted','cancelled')",
            name="ck_svc_service_expense_status",
        ),
        CheckConstraint("amount >= 0", name="ck_svc_service_expense_amount"),
        {"schema": "service"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    work_order_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_work_order.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    request_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("service.svc_service_request.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    expense_type: Mapped[str] = mapped_column(String(40), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    incurred_on: Mapped[date] = mapped_column(Date, nullable=False)
    employee_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_employee.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    is_billable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    finance_journal_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
