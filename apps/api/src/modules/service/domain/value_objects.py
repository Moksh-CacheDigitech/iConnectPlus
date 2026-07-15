"""Service value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ServiceAmount:
    amount: Decimal
    currency_code: str


@dataclass(frozen=True)
class ServiceCodes:
    document_number: str
