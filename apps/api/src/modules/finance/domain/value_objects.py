"""Finance domain value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency_code: str

    def to_base(self, exchange_rate: Decimal) -> Decimal:
        return (self.amount * exchange_rate).quantize(Decimal("0.0001"))


@dataclass(frozen=True)
class ExchangeRate:
    rate: Decimal
    currency_code: str
    base_currency_code: str

    def convert(self, amount: Decimal) -> Decimal:
        return (amount * self.rate).quantize(Decimal("0.0001"))


@dataclass(frozen=True)
class JournalTotals:
    total_debit: Decimal
    total_credit: Decimal
    base_total_debit: Decimal
    base_total_credit: Decimal

    @property
    def is_balanced(self) -> bool:
        return self.total_debit == self.total_credit and self.base_total_debit == self.base_total_credit

    @classmethod
    def from_lines(cls, lines: list) -> "JournalTotals":
        total_debit = Decimal("0")
        total_credit = Decimal("0")
        base_debit = Decimal("0")
        base_credit = Decimal("0")
        for line in lines:
            total_debit += Decimal(str(line.debit_amount))
            total_credit += Decimal(str(line.credit_amount))
            base_debit += Decimal(str(line.base_debit_amount))
            base_credit += Decimal(str(line.base_credit_amount))
        return cls(
            total_debit=total_debit,
            total_credit=total_credit,
            base_total_debit=base_debit,
            base_total_credit=base_credit,
        )
