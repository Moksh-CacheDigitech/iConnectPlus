
"""Payroll value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MoneyAmount:
    value: Decimal
    currency_code: str

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Money amount cannot be negative")
        if not self.currency_code:
            raise ValueError("Currency code required")


@dataclass(frozen=True)
class PaidDays:
    value: Decimal

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Paid days cannot be negative")
