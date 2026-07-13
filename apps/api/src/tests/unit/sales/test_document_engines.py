"""Unit tests for quotation / order / delivery engines."""

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.sales.domain.exceptions import (
    InvalidConversion,
    InvalidDocumentState,
    QuantityExceeded,
)
from modules.sales.domain.value_objects import LineTotals
from modules.sales.service.engines.delivery_engine import DeliveryEngine
from modules.sales.service.engines.order_engine import OrderEngine
from modules.sales.service.engines.quotation_engine import QuotationEngine


class _QLine:
    def __init__(self, qty, price, discount=0, tax_rate=0, discount_percent=0):
        self.quantity = qty
        self.unit_price = price
        self.discount_amount = discount
        self.discount_percent = discount_percent
        self.tax_rate = tax_rate
        self.tax_amount = 0
        self.line_total = 0
        self.is_deleted = False


class _Quotation:
    def __init__(self, status, valid_until=None):
        self.status = status
        self.valid_until = valid_until or (date.today() + timedelta(days=7))


class _OLine:
    def __init__(self, qty, delivered=0, invoiced=0, unit_price=10, status="open"):
        self.id = uuid4()
        self.quantity = qty
        self.quantity_delivered = delivered
        self.quantity_invoiced = invoiced
        self.unit_price = unit_price
        self.status = status
        self.is_deleted = False


class _Order:
    def __init__(self, status, lines):
        self.status = status
        self.lines = lines
        self.delivered_amount = 0
        self.invoiced_amount = 0


class _DLine:
    def __init__(self, order_line_id, quantity):
        self.order_line_id = order_line_id
        self.quantity = quantity
        self.status = "pending"
        self.is_deleted = False


class _Delivery:
    def __init__(self, status, lines):
        self.status = status
        self.lines = lines
        self.subtotal_amount = 0


def test_line_totals_compute() -> None:
    totals = LineTotals.compute(
        quantity=Decimal("10"),
        unit_price=Decimal("100"),
        discount_amount=Decimal("50"),
        tax_rate=Decimal("10"),
    )
    assert totals.line_total == Decimal("1045.0000")


def test_quotation_header_totals() -> None:
    lines = [_QLine(2, 100, discount=10, tax_rate=0), _QLine(1, 50)]
    totals = QuotationEngine().compute_header_totals(lines)
    assert totals.subtotal_amount == Decimal("250.0000")
    assert totals.discount_amount == Decimal("10.0000")
    assert totals.total_amount == Decimal("240.0000")


def test_quotation_convert_requires_accepted() -> None:
    with pytest.raises(InvalidConversion):
        QuotationEngine().validate_convertible(_Quotation("draft"))


def test_quotation_convert_rejects_expired() -> None:
    with pytest.raises(InvalidConversion):
        QuotationEngine().validate_convertible(
            _Quotation("accepted", valid_until=date.today() - timedelta(days=1))
        )


def test_order_remaining_and_confirm() -> None:
    engine = OrderEngine()
    line = _OLine(10, delivered=3)
    assert engine.remaining_to_deliver(line) == Decimal("7")
    order = _Order("draft", [line])
    engine.validate_confirmable(order)
    order_empty = _Order("draft", [])
    with pytest.raises(InvalidDocumentState):
        engine.validate_confirmable(order_empty)


def test_delivery_qty_exceeded() -> None:
    engine = DeliveryEngine()
    line = _OLine(5, delivered=4)
    with pytest.raises(QuantityExceeded):
        engine.validate_delivery_qty(line, Decimal("2"))


def test_confirm_delivery_updates_order() -> None:
    engine = DeliveryEngine()
    line = _OLine(10, delivered=0, unit_price=20)
    order = _Order("confirmed", [line])
    delivery = _Delivery("draft", [_DLine(line.id, 4)])
    engine.confirm_delivery(delivery, order, {line.id: line})
    assert delivery.status == "delivered"
    assert line.quantity_delivered == 4.0
    assert order.status == "partially_delivered"
