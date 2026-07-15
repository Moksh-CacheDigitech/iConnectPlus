"""Unit tests for E-Commerce engines."""

from types import SimpleNamespace

from modules.ecommerce.service.engines import (
    MarketplaceConnectorEngine,
    OrderEngine,
    ProductListingEngine,
    ReturnRequestEngine,
    StoreEngine,
)


def test_store_lifecycle():
    row = SimpleNamespace(status="draft")
    eng = StoreEngine()
    eng.submit(row)
    assert row.status == "submitted"
    eng.approve(row)
    assert row.status == "approved"


def test_product_listing_lifecycle():
    row = SimpleNamespace(status="draft")
    eng = ProductListingEngine()
    eng.submit(row)
    eng.approve(row)
    eng.publish(row)
    assert row.status == "published"


def test_order_lifecycle():
    row = SimpleNamespace(status="new")
    eng = OrderEngine()
    eng.submit(row)
    eng.accept(row)
    assert row.status == "accepted"


def test_return_request_lifecycle():
    row = SimpleNamespace(status="requested")
    eng = ReturnRequestEngine()
    eng.submit(row)
    eng.approve(row)
    assert row.status == "approved"


def test_marketplace_connector_sync():
    row = SimpleNamespace(status="draft")
    eng = MarketplaceConnectorEngine()
    eng.submit(row)
    eng.approve(row)
    eng.sync(row)
    assert row.status == "active"
