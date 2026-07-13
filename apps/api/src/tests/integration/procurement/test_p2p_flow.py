"""Integration-style P2P conversion invariants (no DB)."""

from decimal import Decimal
from uuid import uuid4

from modules.procurement.service.engines.grn_engine import GrnEngine
from modules.procurement.service.engines.order_engine import OrderEngine
from modules.procurement.service.engines.requisition_engine import RequisitionEngine


class _RLine:
    def __init__(self, qty, cost):
        self.quantity = qty
        self.estimated_unit_cost = cost
        self.tax_amount = 0
        self.line_total = qty * cost
        self.is_deleted = False


class _Requisition:
    def __init__(self, status, lines):
        self.status = status
        self.lines = lines
        self.subtotal_amount = 0
        self.tax_amount = 0
        self.total_amount = 0


class _OLine:
    def __init__(self, qty, unit_cost=100):
        self.id = uuid4()
        self.quantity = qty
        self.quantity_received = 0
        self.quantity_invoiced = 0
        self.unit_cost = unit_cost
        self.status = "open"
        self.is_deleted = False


class _Order:
    def __init__(self, status, lines):
        self.status = status
        self.lines = lines
        self.received_amount = 0
        self.invoiced_amount = 0


def test_p2p_requisition_to_order_gate() -> None:
    re = RequisitionEngine()
    req = _Requisition("approved", [_RLine(5, 100)])
    re.validate_convertible(req)
    totals = re.compute_header_totals(req.lines)
    assert totals.total_amount == Decimal("500.0000")


def test_p2p_partial_then_full_grn() -> None:
    oe = OrderEngine()
    ge = GrnEngine()
    line = _OLine(10, unit_cost=50)
    order = _Order("sent", [line])

    ge.validate_receive_qty(line, Decimal("4"))
    oe.apply_receive_qty(line, Decimal("4"))
    oe.refresh_header_amounts(order)
    assert order.status == "partially_received"

    ge.validate_receive_qty(line, Decimal("6"))
    oe.apply_receive_qty(line, Decimal("6"))
    oe.refresh_header_amounts(order)
    assert order.status == "received"
    assert oe.remaining_to_receive(line) == Decimal("0")
