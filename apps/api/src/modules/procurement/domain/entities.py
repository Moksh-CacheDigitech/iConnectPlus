"""Procurement domain entities."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class DocumentTotals:
    subtotal_amount: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal


@dataclass
class GrnReceiptResult:
    grn_id: UUID
    order_id: UUID
    inventory_event_emitted: bool
    stock_updated: bool


@dataclass
class PostingResult:
    document_id: UUID
    finance_ledger_id: UUID
    finance_journal_id: UUID
    posting_status: str
