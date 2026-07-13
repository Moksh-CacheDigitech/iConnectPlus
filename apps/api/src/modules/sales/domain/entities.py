"""Sales domain entities."""

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
class CreditCheckResult:
    customer_id: UUID
    credit_limit: Decimal
    credit_used: Decimal
    credit_available: Decimal
    credit_hold: bool
    approved: bool
