"""E-Commerce module import smoke tests."""

from modules.ecommerce.models import EcOrder, EcProductListing, EcStore
from modules.ecommerce.router import ecommerce_router
from modules.ecommerce.service import (
    EcommerceIntegrationService,
    OrderService,
    ProductListingService,
    StoreService,
)
from modules.ecommerce.service.engines import OrderEngine, ProductListingEngine, StoreEngine


def test_ecommerce_models_importable():
    assert EcStore is not None
    assert EcProductListing is not None
    assert EcOrder is not None


def test_ecommerce_router_mounted():
    assert ecommerce_router.prefix == "/ecommerce"
    assert len(ecommerce_router.routes) > 0


def test_ecommerce_services_and_engines_importable():
    assert StoreService is not None
    assert ProductListingService is not None
    assert OrderService is not None
    assert EcommerceIntegrationService is not None
    assert StoreEngine is not None
    assert ProductListingEngine is not None
    assert OrderEngine is not None
