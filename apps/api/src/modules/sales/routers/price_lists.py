"""Price list routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.sales.dependencies import (
    PaginationParams,
    extract_update_fields,
    get_pagination,
    paginate,
)
from modules.sales.schemas import (
    PriceListCreateRequest,
    PriceListItemCreateRequest,
    PriceListItemResponse,
    PriceListResponse,
    PriceListUpdateRequest,
)
from modules.sales.service.price_list_service import PriceListService
from shared.schemas import APIResponse

price_lists_router = APIRouter(prefix="/price-lists", tags=["Sales - Price Lists"])


@price_lists_router.get("", response_model=APIResponse[list[PriceListResponse]])
def list_price_lists(
    ctx: Annotated[TenantContext, Depends(require_permission("sales.price_list:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[PriceListResponse]]:
    rows = PriceListService(db).list_price_lists(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Price lists retrieved",
        data=[PriceListResponse.model_validate(r) for r in page],
    )


@price_lists_router.post("", response_model=APIResponse[PriceListResponse])
def create_price_list(
    body: PriceListCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.price_list:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PriceListResponse]:
    row = PriceListService(db).create_price_list(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Price list created", data=PriceListResponse.model_validate(row))


@price_lists_router.get("/{price_list_id}", response_model=APIResponse[PriceListResponse])
def get_price_list(
    price_list_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.price_list:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PriceListResponse]:
    row = PriceListService(db).get_price_list(ctx, price_list_id)
    return APIResponse(message="Price list retrieved", data=PriceListResponse.model_validate(row))


@price_lists_router.patch("/{price_list_id}", response_model=APIResponse[PriceListResponse])
def update_price_list(
    price_list_id: UUID,
    body: PriceListUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.price_list:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PriceListResponse]:
    row = PriceListService(db).update_price_list(ctx, price_list_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Price list updated", data=PriceListResponse.model_validate(row))


@price_lists_router.delete("/{price_list_id}", response_model=APIResponse[dict])
def delete_price_list(
    price_list_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.price_list:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    PriceListService(db).delete_price_list(ctx, price_list_id)
    db.commit()
    return APIResponse(message="Price list deleted", data={})


@price_lists_router.post(
    "/{price_list_id}/items", response_model=APIResponse[PriceListItemResponse]
)
def add_price_list_item(
    price_list_id: UUID,
    body: PriceListItemCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.price_list:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PriceListItemResponse]:
    item = PriceListService(db).add_item(ctx, price_list_id, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Price list item added",
        data=PriceListItemResponse.model_validate(item),
    )
