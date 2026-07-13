"""Sales order routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.sales.dependencies import PaginationParams, get_pagination, paginate
from modules.sales.schemas import (
    SalesOrderCreateRequest,
    SalesOrderLineCreateRequest,
    SalesOrderLineResponse,
    SalesOrderResponse,
    WorkflowActionRequest,
)
from modules.sales.service.sales_order_service import SalesOrderService
from shared.schemas import APIResponse

orders_router = APIRouter(prefix="/orders", tags=["Sales - Orders"])


@orders_router.get("", response_model=APIResponse[list[SalesOrderResponse]])
def list_orders(
    ctx: Annotated[TenantContext, Depends(require_permission("sales.order:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[SalesOrderResponse]]:
    rows = SalesOrderService(db).list_orders(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Orders retrieved",
        data=[SalesOrderResponse.model_validate(r) for r in page],
    )


@orders_router.post("", response_model=APIResponse[SalesOrderResponse])
def create_order(
    body: SalesOrderCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.order:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[SalesOrderResponse]:
    row = SalesOrderService(db).create(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Order created", data=SalesOrderResponse.model_validate(row))


@orders_router.get("/{order_id}", response_model=APIResponse[SalesOrderResponse])
def get_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.order:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[SalesOrderResponse]:
    row = SalesOrderService(db).get_order(ctx, order_id)
    return APIResponse(message="Order retrieved", data=SalesOrderResponse.model_validate(row))


@orders_router.post("/{order_id}/lines", response_model=APIResponse[SalesOrderLineResponse])
def add_order_line(
    order_id: UUID,
    body: SalesOrderLineCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.order:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[SalesOrderLineResponse]:
    line = SalesOrderService(db).add_line(ctx, order_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Order line added", data=SalesOrderLineResponse.model_validate(line))


@orders_router.post("/{order_id}/submit", response_model=APIResponse[SalesOrderResponse])
def submit_order(
    order_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.order:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[SalesOrderResponse]:
    row = SalesOrderService(db).submit(ctx, order_id)
    db.commit()
    return APIResponse(message="Order submitted", data=SalesOrderResponse.model_validate(row))


@orders_router.post("/{order_id}/confirm", response_model=APIResponse[SalesOrderResponse])
def confirm_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.order:confirm"))],
    db: Annotated[Session, Depends(get_db)],
    credit_override: Annotated[bool, Query()] = False,
) -> APIResponse[SalesOrderResponse]:
    row = SalesOrderService(db).confirm(ctx, order_id, credit_override=credit_override)
    db.commit()
    return APIResponse(message="Order confirmed", data=SalesOrderResponse.model_validate(row))


@orders_router.post("/{order_id}/cancel", response_model=APIResponse[SalesOrderResponse])
def cancel_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.order:cancel"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[SalesOrderResponse]:
    row = SalesOrderService(db).cancel(ctx, order_id)
    db.commit()
    return APIResponse(message="Order cancelled", data=SalesOrderResponse.model_validate(row))


@orders_router.delete("/{order_id}", response_model=APIResponse[dict])
def delete_order(
    order_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.order:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    SalesOrderService(db).delete(ctx, order_id)
    db.commit()
    return APIResponse(message="Order deleted", data={})
