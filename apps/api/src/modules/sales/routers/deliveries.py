"""Delivery routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.sales.dependencies import PaginationParams, get_pagination, paginate
from modules.sales.schemas import DeliveryCreateRequest, DeliveryResponse
from modules.sales.service.delivery_service import DeliveryService
from shared.schemas import APIResponse

deliveries_router = APIRouter(prefix="/deliveries", tags=["Sales - Deliveries"])


@deliveries_router.get("", response_model=APIResponse[list[DeliveryResponse]])
def list_deliveries(
    ctx: Annotated[TenantContext, Depends(require_permission("sales.delivery:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[DeliveryResponse]]:
    rows = DeliveryService(db).list_deliveries(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Deliveries retrieved",
        data=[DeliveryResponse.model_validate(r) for r in page],
    )


@deliveries_router.post("", response_model=APIResponse[DeliveryResponse])
def create_delivery(
    body: DeliveryCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.delivery:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[DeliveryResponse]:
    row = DeliveryService(db).create_from_order(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Delivery created", data=DeliveryResponse.model_validate(row))


@deliveries_router.get("/{delivery_id}", response_model=APIResponse[DeliveryResponse])
def get_delivery(
    delivery_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.delivery:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[DeliveryResponse]:
    row = DeliveryService(db).get_delivery(ctx, delivery_id)
    return APIResponse(message="Delivery retrieved", data=DeliveryResponse.model_validate(row))


@deliveries_router.post("/{delivery_id}/ship", response_model=APIResponse[DeliveryResponse])
def ship_delivery(
    delivery_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.delivery:ship"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[DeliveryResponse]:
    row = DeliveryService(db).ship(ctx, delivery_id)
    db.commit()
    return APIResponse(message="Delivery shipped", data=DeliveryResponse.model_validate(row))
