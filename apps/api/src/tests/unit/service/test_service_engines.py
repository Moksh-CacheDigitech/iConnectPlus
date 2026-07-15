"""Unit tests for service engines."""

from types import SimpleNamespace

from modules.service.service.engines import (
    ServiceExpenseEngine,
    ServiceRequestEngine,
    ServiceResolutionEngine,
    ServiceWorkOrderEngine,
)


def test_service_request_lifecycle():
    engine = ServiceRequestEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    assert row.status == "submitted"
    engine.approve(row)
    assert row.status == "approved"


def test_work_order_complete():
    engine = ServiceWorkOrderEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.assign(row)
    engine.start(row)
    engine.complete(row)
    assert row.status == "completed"


def test_expense_post():
    engine = ServiceExpenseEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.approve(row)
    engine.post(row)
    assert row.status == "posted"


def test_resolution_complete():
    engine = ServiceResolutionEngine()
    row = SimpleNamespace(status="draft")
    engine.submit(row)
    engine.complete(row)
    assert row.status == "completed"
