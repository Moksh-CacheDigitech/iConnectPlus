"""Unit tests for inventory engines."""

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from modules.inventory.domain.exceptions import InsufficientStock, InvalidDocumentState
from modules.inventory.service.engines import (
    CycleCountEngine,
    ReservationEngine,
    StockEngine,
    ValuationEngine,
)


def _balance(**kwargs):
    defaults = {
        "on_hand_qty": 100,
        "reserved_qty": 20,
        "available_qty": 80,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_stock_engine_receipt_and_available():
    engine = StockEngine()
    bal = _balance()
    engine.apply_receipt(bal, Decimal("10"))
    assert float(bal.on_hand_qty) == 110
    assert float(bal.available_qty) == 90


def test_stock_engine_reserve_blocks_when_insufficient():
    engine = StockEngine()
    bal = _balance(available_qty=5, reserved_qty=0, on_hand_qty=5)
    with pytest.raises(InsufficientStock):
        engine.apply_reserve(bal, Decimal("10"))


def test_stock_engine_issue_against_reservation():
    engine = StockEngine()
    bal = _balance(on_hand_qty=50, reserved_qty=20, available_qty=30)
    engine.apply_issue(bal, Decimal("10"), against_reservation=True)
    assert float(bal.on_hand_qty) == 40
    assert float(bal.reserved_qty) == 10
    assert float(bal.available_qty) == 30


def test_reservation_engine_partial_issue():
    engine = ReservationEngine()
    res = SimpleNamespace(quantity_reserved=100, quantity_issued=0, status="active")
    engine.apply_issue(res, Decimal("40"))
    assert res.status == "partially_issued"
    engine.apply_issue(res, Decimal("60"))
    assert res.status == "fulfilled"


def test_fifo_consume_oldest_first():
    engine = ValuationEngine()
    layers = [
        SimpleNamespace(remaining_qty=10, unit_cost=5, status="open"),
        SimpleNamespace(remaining_qty=20, unit_cost=8, status="open"),
    ]
    result = engine.consume_fifo(layers, Decimal("15"))
    assert float(result.total_cost) == 10 * 5 + 5 * 8
    assert layers[0].status == "depleted"
    assert float(layers[1].remaining_qty) == 15


def test_cycle_count_variance_types():
    engine = CycleCountEngine()
    line = SimpleNamespace(system_qty=10, counted_qty=8, variance_qty=0, variance_type="match")
    engine.compute_variance(line)
    assert line.variance_type == "shortage"
    line.counted_qty = 12
    engine.compute_variance(line)
    assert line.variance_type == "excess"


def test_adjustment_zero_rejected():
    engine = StockEngine()
    bal = _balance()
    with pytest.raises(InvalidDocumentState):
        engine.apply_adjustment(bal, Decimal("0"))


def test_unused_uuid_placeholder():
    assert uuid4() is not None
