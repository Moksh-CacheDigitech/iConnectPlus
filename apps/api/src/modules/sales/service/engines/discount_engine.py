"""Discount application engine."""

from dataclasses import dataclass
from decimal import Decimal

from modules.sales.domain.enums import DiscountType
from modules.sales.models.pricing import SalesDiscountRule


@dataclass(frozen=True)
class DiscountApplication:
    discount_amount: Decimal
    requires_approval: bool
    applied_percent: Decimal | None = None


class DiscountEngine:
    def apply_discount(
        self,
        *,
        base_amount: Decimal,
        rule: SalesDiscountRule,
        discount_percent: Decimal | None = None,
        discount_amount: Decimal | None = None,
    ) -> DiscountApplication:
        requires_approval = bool(rule.requires_approval)
        applied_percent: Decimal | None = None

        if rule.discount_type == DiscountType.PERCENT.value:
            percent = discount_percent if discount_percent is not None else Decimal(
                str(rule.discount_value)
            )
            applied_percent = percent
            amount = (base_amount * percent / Decimal("100")).quantize(Decimal("0.0001"))
            if rule.max_discount_percent is not None and percent > Decimal(
                str(rule.max_discount_percent)
            ):
                requires_approval = True
        elif rule.discount_type == DiscountType.FIXED_AMOUNT.value:
            amount = (
                discount_amount
                if discount_amount is not None
                else Decimal(str(rule.discount_value))
            ).quantize(Decimal("0.0001"))
            if base_amount > 0:
                applied_percent = (amount / base_amount * Decimal("100")).quantize(
                    Decimal("0.0001")
                )
                if rule.max_discount_percent is not None and applied_percent > Decimal(
                    str(rule.max_discount_percent)
                ):
                    requires_approval = True
        else:
            amount = Decimal("0")

        if amount > base_amount:
            amount = base_amount

        return DiscountApplication(
            discount_amount=amount,
            requires_approval=requires_approval,
            applied_percent=applied_percent,
        )
