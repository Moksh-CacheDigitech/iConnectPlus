"""Integration-style O2C conversion invariants (no DB)."""

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.sales.domain.exceptions import InvalidConversion, QuantityExceeded
from modules.sales.service.engines.delivery_engine import DeliveryEngine
from modules.sales.service.engines.order_engine import OrderEngine
from modules.sales.service.engines.quotation_engine import QuotationEngine


class _QLine:
    def __init__(self, qty, price):
        self.quantity = qty
        self.unit_price = price
        self.discount_amount = 0
        self.discount_percent = 0
        self.tax_rate = 0
        self.tax_amount = 0
        self.line_total = qty * price
        self.is_deleted = False


class _Quotation:
    def __init__(self, status, lines, valid_until=None):
        self.status = status
        self.lines = lines
        self.valid_until = valid_until or (date.today() + timedelta(days=14))
        self.subtotal_amount = 0
        self.discount_amount = 0
        self.tax_amount = 0
        self.total_amount = 0


class _OLine:
    def __init__(self, qty, unit_price=100):
        self.id = uuid4()
        self.quantity = qty
        self.quantity_delivered = 0
        self.quantity_invoiced = 0
        self.unit_price = unit_price
        self.status = "open"
        self.is_deleted = False


class _Order:
    def __init__(self, status, lines):
        self.status = status
        self.lines = lines
        self.delivered_amount = 0
        self.invoiced_amount = 0


def test_o2c_quotation_to_order_gate() -> None:
    qe = QuotationEngine()
    quotation = _Quotation("accepted", [_QLine(5, 100)])
    qe.validate_convertible(quotation)
    totals = qe.compute_header_totals(quotation.lines)
    assert totals.total_amount == Decimal("500.0000")


def test_o2c_partial_then_full_delivery() -> None:
    oe = OrderEngine()
    de = DeliveryEngine()
    line = _OLine(10, unit_price=50)
    order = _Order("confirmed", [line])

    de.validate_delivery_qty(line, Decimal("4"))
    oe.apply_delivery_qty(line, Decimal("4"))
    oe.refresh_header_amounts(order)
    assert order.status == "partially_delivered"
    assert order.delivered_amount == 200.0

    de.validate_delivery_qty(line, Decimal("6"))
    oe.apply_delivery_qty(line, Decimal("6"))
    oe.refresh_header_amounts(order)
    assert order.status == "delivered"
    assert line.quantity_delivered == 10.0

    with pytest.raises(QuantityExceeded):
        de.validate_delivery_qty(line, Decimal("1"))


def test_o2c_rejects_draft_quotation_conversion() -> None:
    with pytest.raises(InvalidConversion):
        QuotationEngine().validate_convertible(
            _Quotation("draft", [_QLine(1, 10)])
        )
