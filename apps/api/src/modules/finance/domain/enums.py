"""Finance domain enums."""

from enum import Enum


class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class NormalBalance(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class JournalType(str, Enum):
    MANUAL = "manual"
    SYSTEM = "system"
    ADJUSTMENT = "adjustment"
    REVERSAL = "reversal"


class JournalStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    POSTED = "posted"
    REVERSED = "reversed"
    CANCELLED = "cancelled"


class PeriodStatus(str, Enum):
    OPEN = "open"
    SOFT_CLOSED = "soft_closed"
    HARD_CLOSED = "hard_closed"


class FiscalYearStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class SubLedgerDocumentType(str, Enum):
    INVOICE = "invoice"
    DEBIT_NOTE = "debit_note"
    CREDIT_NOTE = "credit_note"
    PAYMENT = "payment"
    ADJUSTMENT = "adjustment"


class FinanceEntityType(str, Enum):
    JOURNAL = "journal"
    GL_ENTRY = "gl_entry"
    CUSTOMER_LEDGER = "customer_ledger"
    VENDOR_LEDGER = "vendor_ledger"
    TAX_REGISTER = "tax_register"
    ASSET_TRANSACTION = "asset_transaction"


CODE_PREFIXES: dict[FinanceEntityType, tuple[str, int]] = {
    FinanceEntityType.JOURNAL: ("JE-", 8),
    FinanceEntityType.GL_ENTRY: ("GL-", 8),
    FinanceEntityType.CUSTOMER_LEDGER: ("AR-", 8),
    FinanceEntityType.VENDOR_LEDGER: ("AP-", 8),
    FinanceEntityType.TAX_REGISTER: ("TAX-", 8),
    FinanceEntityType.ASSET_TRANSACTION: ("AT-", 8),
}

WORKFLOW_CODES: dict[str, str] = {
    "fin_journal_header": "FIN_JOURNAL_APPROVAL",
    "fin_vendor_ledger": "FIN_VENDOR_PAYMENT",
    "fin_asset_transaction": "FIN_ASSET_POSTING",
}
