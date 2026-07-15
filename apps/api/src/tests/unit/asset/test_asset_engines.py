"""Unit tests for asset engines."""

from types import SimpleNamespace

from modules.asset.service.engines import (
    AssetAssignmentEngine,
    AssetDepreciationEngine,
    AssetDisposalEngine,
    AssetEngine,
    AssetMaintenanceEngine,
)


def test_asset_lifecycle():
    engine = AssetEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"
    engine.activate(row)
    assert row.status == "active"


def test_assignment_return():
    engine = AssetAssignmentEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.activate(row)
    engine.return_assignment(row)
    assert row.status == "returned"


def test_maintenance_complete():
    engine = AssetMaintenanceEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.start(row)
    engine.complete(row)
    assert row.status == "completed"


def test_depreciation_and_disposal():
    dep = AssetDepreciationEngine()
    drow = SimpleNamespace(status="draft")
    dep.calculate(drow)
    dep.post(drow)
    assert drow.status == "posted"

    disp = AssetDisposalEngine()
    xrow = SimpleNamespace(status="draft")
    disp.submit(xrow)
    disp.approve(xrow)
    disp.post(xrow)
    assert xrow.status == "posted"
