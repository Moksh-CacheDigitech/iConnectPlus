"""Organization module router aggregation."""

from fastapi import APIRouter

from modules.organization.routers.companies import router as companies_router
from modules.organization.routers.hierarchy import (
    branches_router,
    business_units_router,
    cost_centers_router,
    departments_router,
    locations_router,
    profit_centers_router,
)
from modules.organization.routers.org_tree import context_router, tree_router

organization_router = APIRouter()
organization_router.include_router(companies_router)
organization_router.include_router(branches_router)
organization_router.include_router(departments_router)
organization_router.include_router(business_units_router)
organization_router.include_router(locations_router)
organization_router.include_router(cost_centers_router)
organization_router.include_router(profit_centers_router)
organization_router.include_router(tree_router)
organization_router.include_router(context_router)
