"""Journal entry ORM models."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from modules.finance.models.mixins import FinanceTransactionMixin


class FinJournalHeader(Base, *FinanceTransactionMixin):
    __tablename__ = "fin_journal_header"
    __table_args__ = (
        UniqueConstraint("company_id", "journal_number", name="uk_fin_journal_header_company_number"),
        CheckConstraint(
            "status != 'posted' OR total_debit = total_credit",
            name="ck_fin_journal_header_balanced",
        ),
        CheckConstraint(
            "total_debit >= 0 AND total_credit >= 0",
            name="ck_fin_journal_header_amounts",
        ),
        CheckConstraint(
            "journal_type IN ('manual','system','adjustment','reversal')",
            name="ck_fin_journal_header_type",
        ),
        CheckConstraint(
            "status IN ('draft','submitted','approved','posted','reversed','cancelled')",
            name="ck_fin_journal_header_status",
        ),
        CheckConstraint(
            "workflow_status IN ('pending','in_progress','approved','rejected')",
            name="ck_fin_journal_header_workflow_status",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    journal_number: Mapped[str] = mapped_column(String(50), nullable=False)
    journal_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    journal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    fiscal_year_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_fiscal_year.id", ondelete="RESTRICT"),
        nullable=False,
    )
    period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    total_debit: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_credit: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft", index=True)
    workflow_status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    workflow_instance_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.wf_instance.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_by: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.sec_user.id", ondelete="RESTRICT"),
        nullable=True,
    )
    reversal_of_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    source_module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_document_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_document_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    lines: Mapped[list["FinJournalLine"]] = relationship(
        back_populates="journal_header",
        cascade="all, delete-orphan",
    )


class FinJournalLine(Base, *FinanceTransactionMixin):
    __tablename__ = "fin_journal_line"
    __table_args__ = (
        UniqueConstraint(
            "journal_header_id",
            "line_number",
            name="uk_fin_journal_line_header_number",
        ),
        CheckConstraint(
            "(debit_amount > 0 AND credit_amount = 0) OR "
            "(credit_amount > 0 AND debit_amount = 0)",
            name="ck_fin_journal_line_dc",
        ),
        CheckConstraint(
            "debit_amount >= 0 AND credit_amount >= 0",
            name="ck_fin_journal_line_amounts",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    journal_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_chart_of_account.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    debit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    credit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    base_debit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    base_credit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    cost_center_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_cost_center.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    profit_center_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_profit_center.id", ondelete="RESTRICT"),
        nullable=True,
    )
    customer_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    vendor_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    tax_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_tax.id", ondelete="RESTRICT"),
        nullable=True,
    )
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    journal_header: Mapped[FinJournalHeader] = relationship(back_populates="lines")
