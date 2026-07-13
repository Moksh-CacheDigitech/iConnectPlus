"""Procurement vendor performance routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.dependencies import PaginationParams, get_pagination, paginate
from modules.procurement.schemas import PerformanceResponse
from modules.procurement.service.performance_service import PerformanceService
from shared.schemas import APIResponse

performance_router = APIRouter(prefix="/performance", tags=["Procurement - Performance"])


@performance_router.get("", response_model=APIResponse[list[PerformanceResponse]])
def list_performance(
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.performance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    vendor_id: Annotated[UUID | None, Query()] = None,
) -> APIResponse[list[PerformanceResponse]]:
    rows = PerformanceService(db).list_performance(ctx, company_id, vendor_id=vendor_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Vendor performance retrieved",
        data=[PerformanceResponse.model_validate(r) for r in page],
    )


@performance_router.get("/{performance_id}", response_model=APIResponse[PerformanceResponse])
def get_performance(
    performance_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.performance:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PerformanceResponse]:
    row = PerformanceService(db).get_performance(ctx, performance_id)
    return APIResponse(
        message="Vendor performance retrieved", data=PerformanceResponse.model_validate(row)
    )
