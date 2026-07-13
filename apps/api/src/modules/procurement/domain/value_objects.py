"""Procurement domain value objects."""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency_code: str

    def to_base(self, exchange_rate: Decimal) -> Decimal:
        return (self.amount * exchange_rate).quantize(Decimal("0.0001"))


@dataclass(frozen=True)
class DocumentNumber:
    value: str


@dataclass(frozen=True)
class LineTotals:
    quantity: Decimal
    unit_cost: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    line_total: Decimal

    @classmethod
    def compute(
        cls,
        quantity: Decimal,
        unit_cost: Decimal,
        discount_amount: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0"),
    ) -> "LineTotals":
        net = (quantity * unit_cost) - discount_amount
        if net < 0:
            net = Decimal("0")
        tax_amount = (net * tax_rate / Decimal("100")).quantize(Decimal("0.0001"))
        line_total = (net + tax_amount).quantize(Decimal("0.0001"))
        return cls(
            quantity=quantity,
            unit_cost=unit_cost,
            discount_amount=discount_amount.quantize(Decimal("0.0001")),
            tax_amount=tax_amount,
            line_total=line_total,
        )


@dataclass(frozen=True)
class ComparisonScore:
    quotation_id: UUID
    price_score: Decimal
    delivery_score: Decimal
    overall_score: Decimal
