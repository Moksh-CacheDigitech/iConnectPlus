"""Unit tests for sales pricing engine."""

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.sales.domain.exceptions import PricingNotFound
from modules.sales.service.engines.pricing_engine import PricingEngine


class _Item:
    def __init__(self, product_id, unit_price, min_quantity=1, status="active"):
        self.product_id = product_id
        self.unit_price = unit_price
        self.min_quantity = min_quantity
        self.status = status
        self.is_deleted = False


class _PriceList:
    def __init__(
        self,
        price_list_type,
        items,
        *,
        priority=100,
        customer_id=None,
        status="active",
        effective_from=None,
        effective_to=None,
    ):
        self.id = uuid4()
        self.price_list_type = price_list_type
        self.items = items
        self.priority = priority
        self.customer_id = customer_id
        self.status = status
        self.effective_from = effective_from or date.today() - timedelta(days=30)
        self.effective_to = effective_to


def test_pricing_prefers_contract_over_standard() -> None:
    product_id = uuid4()
    customer_id = uuid4()
    lists = [
        _PriceList("standard", [_Item(product_id, 100)]),
        _PriceList("contract", [_Item(product_id, 80)], customer_id=customer_id),
    ]
    result = PricingEngine().resolve_price(
        product_id=product_id,
        quantity=Decimal("1"),
        price_lists=lists,
        customer_id=customer_id,
    )
    assert result.unit_price == Decimal("80")
    assert result.source == "contract"


def test_pricing_volume_break_uses_highest_min_qty() -> None:
    product_id = uuid4()
    lists = [
        _PriceList(
            "volume",
            [
                _Item(product_id, 50, min_quantity=1),
                _Item(product_id, 40, min_quantity=10),
                _Item(product_id, 35, min_quantity=50),
            ],
        )
    ]
    result = PricingEngine().resolve_price(
        product_id=product_id,
        quantity=Decimal("25"),
        price_lists=lists,
    )
    assert result.unit_price == Decimal("40")


def test_pricing_not_found_raises() -> None:
    with pytest.raises(PricingNotFound):
        PricingEngine().resolve_price(
            product_id=uuid4(),
            quantity=Decimal("1"),
            price_lists=[],
        )
