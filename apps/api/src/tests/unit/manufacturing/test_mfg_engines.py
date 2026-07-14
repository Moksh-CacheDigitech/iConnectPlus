"""Unit tests for manufacturing engines."""

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from modules.manufacturing.domain.exceptions import (
    InvalidBomState,
    InvalidProductionOrderState,
    InvalidScrapState,
    InvalidWipState,
)
from modules.manufacturing.service.engines import (
    BomEngine,
    ProductionEngine,
    ScrapEngine,
    VarianceEngine,
    WipEngine,
)


def test_bom_explode_with_scrap():
    engine = BomEngine()
    bom = SimpleNamespace(
        status="active",
        lines=[
            SimpleNamespace(
                id=uuid4(),
                is_deleted=False,
                status="active",
                component_product_id=uuid4(),
                quantity=2,
                uom_id=uuid4(),
                scrap_percent=10,
                alternate_product_id=None,
                is_optional=False,
            )
        ],
    )
    reqs = engine.explode(bom, Decimal("10"))
    assert len(reqs) == 1
    assert float(reqs[0].quantity) == 20
    assert float(reqs[0].required_qty) == 22


def test_bom_activate_requires_lines():
    engine = BomEngine()
    bom = SimpleNamespace(status="draft", lines=[])
    with pytest.raises(InvalidBomState):
        engine.validate_activatable(bom)


def test_wip_add_and_relieve():
    engine = WipEngine()
    wip = SimpleNamespace(
        status="open", material_cost=0, labor_cost=0, overhead_cost=0, total_cost=0
    )
    engine.add_material(wip, Decimal("100"))
    assert float(wip.material_cost) == 100
    assert float(wip.total_cost) == 100
    engine.relieve_material(wip, Decimal("40"))
    assert float(wip.material_cost) == 60


def test_wip_proportional_relief():
    engine = WipEngine()
    wip = SimpleNamespace(
        status="open", material_cost=80, labor_cost=20, overhead_cost=0, total_cost=100
    )
    relieved = engine.relieve_proportional(wip, Decimal("0.5"))
    assert float(relieved) == 50
    assert float(wip.total_cost) == 50


def test_wip_closed_blocks_add():
    engine = WipEngine()
    wip = SimpleNamespace(status="closed", material_cost=0, labor_cost=0, overhead_cost=0, total_cost=0)
    with pytest.raises(InvalidWipState):
        engine.add_material(wip, Decimal("10"))


def test_production_engine_lifecycle():
    engine = ProductionEngine()
    order = SimpleNamespace(
        status="draft",
        planned_qty=10,
        completed_qty=0,
        scrapped_qty=0,
        actual_start=None,
        actual_end=None,
    )
    engine.validate_releasable(order)
    order.status = "released"
    engine.apply_start(order)
    assert order.status == "in_progress"
    engine.apply_complete(order)
    assert order.status == "completed"
    engine.apply_close(order)
    assert order.status == "closed"


def test_production_engine_cancel_blocked_when_closed():
    engine = ProductionEngine()
    order = SimpleNamespace(status="closed")
    with pytest.raises(InvalidProductionOrderState):
        engine.validate_cancellable(order)


def test_scrap_engine_post_requires_period():
    engine = ScrapEngine()
    scrap = SimpleNamespace(status="approved", period_id=None, quantity=1, unit_cost=5)
    with pytest.raises(InvalidScrapState):
        engine.validate_postable(scrap)


def test_variance_engine_amount():
    engine = VarianceEngine()
    result = engine.compute(
        variance_type="material",
        standard_amount=Decimal("100"),
        actual_amount=Decimal("120"),
    )
    assert float(result.variance_amount) == 20
