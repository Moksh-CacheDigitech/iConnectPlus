"""Sales module router aggregation."""

from fastapi import APIRouter

from modules.sales.routers import (
    customer_credit_router,
    deliveries_router,
    discount_rules_router,
    invoices_router,
    orders_router,
    price_lists_router,
    quotations_router,
    returns_router,
)

sales_router = APIRouter(prefix="/sales")
sales_router.include_router(price_lists_router)
sales_router.include_router(discount_rules_router)
sales_router.include_router(customer_credit_router)
sales_router.include_router(quotations_router)
sales_router.include_router(orders_router)
sales_router.include_router(deliveries_router)
sales_router.include_router(invoices_router)
sales_router.include_router(returns_router)
