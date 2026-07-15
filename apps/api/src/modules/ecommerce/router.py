"""E-Commerce module router aggregation."""

from fastapi import APIRouter

from modules.ecommerce.routers import (
    cart_items_router,
    coupons_router,
    customer_carts_router,
    listing_inventories_router,
    listing_prices_router,
    marketplace_connectors_router,
    notifications_router,
    order_items_router,
    orders_router,
    payment_transactions_router,
    payments_router,
    product_listings_router,
    promotions_router,
    reports_router,
    return_items_router,
    return_requests_router,
    sales_channels_router,
    shipments_router,
    shipping_trackings_router,
    stores_router,
)

ecommerce_router = APIRouter(prefix="/ecommerce")
ecommerce_router.include_router(stores_router)
ecommerce_router.include_router(sales_channels_router)
ecommerce_router.include_router(product_listings_router)
ecommerce_router.include_router(listing_prices_router)
ecommerce_router.include_router(listing_inventories_router)
ecommerce_router.include_router(customer_carts_router)
ecommerce_router.include_router(cart_items_router)
ecommerce_router.include_router(orders_router)
ecommerce_router.include_router(order_items_router)
ecommerce_router.include_router(payments_router)
ecommerce_router.include_router(payment_transactions_router)
ecommerce_router.include_router(shipments_router)
ecommerce_router.include_router(shipping_trackings_router)
ecommerce_router.include_router(return_requests_router)
ecommerce_router.include_router(return_items_router)
ecommerce_router.include_router(coupons_router)
ecommerce_router.include_router(promotions_router)
ecommerce_router.include_router(marketplace_connectors_router)
ecommerce_router.include_router(notifications_router)
ecommerce_router.include_router(reports_router)
