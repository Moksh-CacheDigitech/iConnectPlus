"""Inventory module router aggregation."""

from fastapi import APIRouter

from modules.inventory.routers import (
    adjustments_router,
    batches_router,
    bins_router,
    cycle_counts_router,
    policies_router,
    reports_router,
    reservations_router,
    serials_router,
    stock_router,
    transfers_router,
    valuation_router,
)

inventory_router = APIRouter(prefix="/inventory")
inventory_router.include_router(stock_router)
inventory_router.include_router(bins_router)
inventory_router.include_router(batches_router)
inventory_router.include_router(serials_router)
inventory_router.include_router(reservations_router)
inventory_router.include_router(transfers_router)
inventory_router.include_router(adjustments_router)
inventory_router.include_router(cycle_counts_router)
inventory_router.include_router(policies_router)
inventory_router.include_router(valuation_router)
inventory_router.include_router(reports_router)
