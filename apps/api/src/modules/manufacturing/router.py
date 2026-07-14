"""Manufacturing module router aggregation."""

from fastapi import APIRouter

from modules.manufacturing.routers import (
    boms_router,
    issues_router,
    machines_router,
    orders_router,
    receipts_router,
    reports_router,
    returns_router,
    routings_router,
    scrap_router,
    variances_router,
    wip_router,
    work_centers_router,
)

manufacturing_router = APIRouter(prefix="/manufacturing")
manufacturing_router.include_router(boms_router)
manufacturing_router.include_router(routings_router)
manufacturing_router.include_router(work_centers_router)
manufacturing_router.include_router(machines_router)
manufacturing_router.include_router(orders_router)
manufacturing_router.include_router(issues_router)
manufacturing_router.include_router(returns_router)
manufacturing_router.include_router(receipts_router)
manufacturing_router.include_router(scrap_router)
manufacturing_router.include_router(wip_router)
manufacturing_router.include_router(variances_router)
manufacturing_router.include_router(reports_router)
