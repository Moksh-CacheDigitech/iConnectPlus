"""General ledger and sub-ledger ORM models."""

from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.finance.models.mixins import FinancePostedLedgerMixin, FinanceTransactionMixin


class FinGlEntry(Base, *FinancePostedLedgerMixin):
    __tablename__ = "fin_gl_entry"
    __table_args__ = (
        UniqueConstraint("company_id", "entry_number", name="uk_fin_gl_entry_company_number"),
        CheckConstraint(
            "(debit_amount > 0 AND credit_amount = 0) OR "
            "(credit_amount > 0 AND debit_amount = 0)",
            name="ck_fin_gl_entry_dc",
        ),
        Index("ix_comp_fin_gl_account_period", "company_id", "account_id", "period_id"),
        Index("ix_comp_fin_gl_company_date", "company_id", "entry_date", "account_id"),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    entry_number: Mapped[str] = mapped_column(String(50), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_period.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fiscal_year_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_fiscal_year.id", ondelete="RESTRICT"),
        nullable=False,
    )
    journal_header_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    journal_line_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_line.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_chart_of_account.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    account_code: Mapped[str] = mapped_column(String(50), nullable=False)
    debit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    credit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    base_debit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    base_credit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cost_center_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_cost_center.id", ondelete="RESTRICT"),
        nullable=True,
    )
    profit_center_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization.org_profit_center.id", ondelete="RESTRICT"),
        nullable=True,
    )
    is_reversal: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    posted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    posted_by: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("foundation.sec_user.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)


class FinCustomerLedger(Base, *FinanceTransactionMixin):
    __tablename__ = "fin_customer_ledger"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "document_number",
            name="uk_fin_customer_ledger_company_number",
        ),
        CheckConstraint(
            "status IN ('open','partial','paid','written_off','cancelled')",
            name="ck_fin_customer_ledger_status",
        ),
        Index("ix_fin_customer_ledger_company_customer_due", "company_id", "customer_id", "due_date"),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_customer.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    debit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    credit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    balance_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    journal_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    source_module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_document_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    aging_bucket: Mapped[str | None] = mapped_column(String(20), nullable=True)


class FinVendorLedger(Base, *FinanceTransactionMixin):
    __tablename__ = "fin_vendor_ledger"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "document_number",
            name="uk_fin_vendor_ledger_company_number",
        ),
        CheckConstraint(
            "status IN ('open','partial','paid','written_off','cancelled')",
            name="ck_fin_vendor_ledger_status",
        ),
        Index("ix_fin_vendor_ledger_company_vendor_due", "company_id", "vendor_id", "due_date"),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("master.master_vendor.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    document_number: Mapped[str] = mapped_column(String(50), nullable=False)
    document_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(30), nullable=False)
    credit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    debit_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    balance_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open", index=True)
    workflow_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    journal_header_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("finance.fin_journal_header.id", ondelete="RESTRICT"),
        nullable=True,
    )
    source_module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_document_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    aging_bucket: Mapped[str | None] = mapped_column(String(20), nullable=True)
