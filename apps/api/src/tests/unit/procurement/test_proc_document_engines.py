"""Unit tests for procurement document engines."""

from decimal import Decimal
from uuid import uuid4

import pytest

from modules.procurement.domain.exceptions import (
    InvalidDocumentState,
    QuantityExceeded,
)
from modules.procurement.domain.value_objects import LineTotals
from modules.procurement.service.engines.grn_engine import GrnEngine
from modules.procurement.service.engines.order_engine import OrderEngine
from modules.procurement.service.engines.requisition_engine import RequisitionEngine


class _RLine:
    def __init__(self, qty, cost, tax_rate=0):
        self.quantity = qty
        self.estimated_unit_cost = cost
        self.tax_amount = 0
        self.line_total = 0
        self.is_deleted = False


class _Requisition:
    def __init__(self, status, lines):
        self.status = status
        self.lines = lines
        self.subtotal_amount = 0
        self.tax_amount = 0
        self.total_amount = 0


class _OLine:
    def __init__(self, qty, received=0, unit_cost=10, status="open"):
        self.id = uuid4()
        self.quantity = qty
        self.quantity_received = received
        self.quantity_invoiced = 0
        self.unit_cost = unit_cost
        self.status = status
        self.is_deleted = False


class _Order:
    def __init__(self, status, lines):
        self.status = status
        self.lines = lines
        self.received_amount = 0
        self.invoiced_amount = 0


class _GLine:
    def __init__(self, order_line_id, quantity):
        self.order_line_id = order_line_id
        self.quantity = quantity
        self.status = "pending"
        self.is_deleted = False


class _Grn:
    def __init__(self, status, lines):
        self.status = status
        self.lines = lines
        self.subtotal_amount = 0


def test_line_totals_compute_unit_cost() -> None:
    totals = LineTotals.compute(
        quantity=Decimal("10"),
        unit_cost=Decimal("100"),
        discount_amount=Decimal("50"),
        tax_rate=Decimal("10"),
    )
    assert totals.line_total == Decimal("1045.0000")


def test_requisition_convertible_requires_approved() -> None:
    engine = RequisitionEngine()
    req = _Requisition("draft", [_RLine(1, 100)])
    with pytest.raises(InvalidDocumentState):
        engine.validate_convertible(req)


def test_requisition_convertible_ok() -> None:
    engine = RequisitionEngine()
    req = _Requisition("approved", [_RLine(2, 50)])
    engine.validate_convertible(req)
    totals = engine.compute_header_totals(req.lines)
    assert totals.subtotal_amount == Decimal("100.0000")


def test_order_partial_then_full_receive() -> None:
    oe = OrderEngine()
    ge = GrnEngine()
    line = _OLine(10, unit_cost=50)
    order = _Order("sent", [line])

    ge.validate_receive_qty(line, Decimal("4"))
    oe.apply_receive_qty(line, Decimal("4"))
    oe.refresh_header_amounts(order)
    assert order.status == "partially_received"
    assert order.received_amount == 200.0

    ge.validate_receive_qty(line, Decimal("6"))
    oe.apply_receive_qty(line, Decimal("6"))
    oe.refresh_header_amounts(order)
    assert order.status == "received"


def test_order_receive_exceeds_remaining() -> None:
    ge = GrnEngine()
    line = _OLine(5, received=3)
    with pytest.raises(QuantityExceeded):
        ge.validate_receive_qty(line, Decimal("3"))


def test_grn_confirm_requires_lines() -> None:
    ge = GrnEngine()
    grn = _Grn("draft", [])
    order = _Order("sent", [_OLine(5)])
    with pytest.raises(InvalidDocumentState):
        ge.confirm_grn(grn, order, {})
