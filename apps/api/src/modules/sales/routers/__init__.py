"""Sales routers package."""

from modules.sales.routers.customer_credit import customer_credit_router
from modules.sales.routers.deliveries import deliveries_router
from modules.sales.routers.discount_rules import discount_rules_router
from modules.sales.routers.invoices import invoices_router
from modules.sales.routers.orders import orders_router
from modules.sales.routers.price_lists import price_lists_router
from modules.sales.routers.quotations import quotations_router
from modules.sales.routers.returns import returns_router

__all__ = [
    "price_lists_router",
    "discount_rules_router",
    "customer_credit_router",
    "quotations_router",
    "orders_router",
    "deliveries_router",
    "invoices_router",
    "returns_router",
]
