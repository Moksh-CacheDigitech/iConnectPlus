"""Finance Pydantic schemas."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccountGroupCreateRequest(BaseModel):
    group_code: str
    group_name: str
    account_type: str
    parent_group_id: UUID | None = None
    display_order: int = 1
    status: str = "active"


class AccountGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    group_code: str
    group_name: str
    account_type: str
    status: str


class ChartOfAccountCreateRequest(BaseModel):
    account_group_id: UUID
    account_code: str
    account_name: str
    account_type: str
    normal_balance: str
    parent_account_id: UUID | None = None
    is_posting_account: bool = True
    is_cost_center_enabled: bool = False
    is_profit_center_enabled: bool = False
    currency_code: str | None = None
    status: str = "draft"


class ChartOfAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    account_group_id: UUID
    account_code: str
    account_name: str
    account_type: str
    normal_balance: str
    is_posting_account: bool
    status: str
    version: int


class FiscalYearCreateRequest(BaseModel):
    fiscal_year_code: str
    fiscal_year_name: str
    start_date: date
    end_date: date


class FiscalYearResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    fiscal_year_code: str
    fiscal_year_name: str
    start_date: date
    end_date: date
    status: str


class PeriodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    fiscal_year_id: UUID
    period_number: int
    period_name: str
    start_date: date
    end_date: date
    status: str
    ar_closed: bool
    ap_closed: bool
    gl_closed: bool


class PeriodCloseFlagsRequest(BaseModel):
    ar_closed: bool | None = None
    ap_closed: bool | None = None
    inventory_closed: bool | None = None
    payroll_closed: bool | None = None
    gl_closed: bool | None = None


class JournalCreateRequest(BaseModel):
    branch_id: UUID
    journal_date: date
    description: str
    journal_type: str = "manual"
    currency_code: str = "INR"
    exchange_rate: float = 1.0
    period_id: UUID | None = None
    company_id: UUID | None = None


class JournalLineCreateRequest(BaseModel):
    line_number: int
    account_id: UUID
    debit_amount: float = 0
    credit_amount: float = 0
    description: str | None = None
    cost_center_id: UUID | None = None
    tax_id: UUID | None = None
    customer_id: UUID | None = None
    vendor_id: UUID | None = None


class JournalLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    account_id: UUID
    debit_amount: float
    credit_amount: float
    base_debit_amount: float
    base_credit_amount: float


class JournalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    branch_id: UUID
    journal_number: str
    journal_date: date
    journal_type: str
    description: str
    total_debit: float
    total_credit: float
    status: str
    workflow_status: str
    workflow_instance_id: UUID | None = None
    lines: list[JournalLineResponse] = Field(default_factory=list)


class GlEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entry_number: str
    entry_date: date
    account_id: UUID
    account_code: str
    debit_amount: float
    credit_amount: float
    base_debit_amount: float
    base_credit_amount: float


class CustomerLedgerCreateRequest(BaseModel):
    branch_id: UUID
    customer_id: UUID
    document_date: date
    due_date: date
    document_type: str
    debit_amount: float = 0
    credit_amount: float = 0
    currency_code: str = "INR"
    company_id: UUID | None = None


class CustomerLedgerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    document_number: str
    document_date: date
    due_date: date
    balance_amount: float
    status: str
    aging_bucket: str | None = None


class VendorLedgerCreateRequest(BaseModel):
    branch_id: UUID
    vendor_id: UUID
    document_date: date
    due_date: date
    document_type: str
    credit_amount: float = 0
    debit_amount: float = 0
    currency_code: str = "INR"
    company_id: UUID | None = None


class VendorLedgerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    vendor_id: UUID
    document_number: str
    document_date: date
    due_date: date
    balance_amount: float
    status: str
    aging_bucket: str | None = None


class PaymentRequest(BaseModel):
    amount: float


class CurrencyRateCreateRequest(BaseModel):
    currency_id: UUID
    currency_code: str
    base_currency_code: str
    exchange_rate: float
    rate_type: str = "manual"
    effective_from: date
    effective_to: date | None = None
    status: str = "active"
    company_id: UUID | None = None


class CurrencyRateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    currency_code: str
    base_currency_code: str
    exchange_rate: float
    effective_from: date
    effective_to: date | None
    status: str


class AssetTransactionCreateRequest(BaseModel):
    branch_id: UUID
    asset_id: UUID
    transaction_date: date
    transaction_type: str
    amount: float
    period_id: UUID
    currency_code: str = "INR"
    description: str | None = None
    company_id: UUID | None = None


class AssetTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_number: str
    asset_id: UUID
    transaction_type: str
    amount: float
    status: str


class TaxRegisterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    register_number: str
    register_date: date
    tax_type: str
    transaction_type: str
    taxable_amount: float
    tax_amount: float
    status: str


class TrialBalanceLineResponse(BaseModel):
    account_id: UUID
    account_code: str
    account_name: str
    debit_total: float
    credit_total: float
    balance: float


class WorkflowActionRequest(BaseModel):
    comments: str | None = None
