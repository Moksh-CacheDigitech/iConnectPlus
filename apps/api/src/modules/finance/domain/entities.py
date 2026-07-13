"""Finance domain entities."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass
class TrialBalanceLine:
    account_id: UUID
    account_code: str
    account_name: str
    debit_total: Decimal
    credit_total: Decimal
    balance: Decimal


@dataclass
class AccountStatementLine:
    entry_date: date
    entry_number: str
    description: str | None
    debit_amount: Decimal
    credit_amount: Decimal
    running_balance: Decimal


@dataclass
class AgingLine:
    party_id: UUID
    document_number: str
    due_date: date
    balance_amount: Decimal
    aging_bucket: str
