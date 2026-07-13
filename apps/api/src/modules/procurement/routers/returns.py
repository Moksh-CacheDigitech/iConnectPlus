"""Procurement purchase return routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.dependencies import PaginationParams, get_pagination, paginate
from modules.procurement.schemas import (
    ReturnCreateRequest,
    ReturnLineCreateRequest,
    ReturnLineResponse,
    ReturnPostRequest,
    ReturnResponse,
    WorkflowActionRequest,
)
from modules.procurement.service.procurement_posting_service import ProcurementPostingService
from modules.procurement.service.return_service import ReturnService
from shared.schemas import APIResponse

returns_router = APIRouter(prefix="/returns", tags=["Procurement - Returns"])


@returns_router.get("", response_model=APIResponse[list[ReturnResponse]])
def list_returns(
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.return:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[ReturnResponse]]:
    rows = ReturnService(db).list_returns(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Returns retrieved",
        data=[ReturnResponse.model_validate(r) for r in page],
    )


@returns_router.post("", response_model=APIResponse[ReturnResponse])
def create_return(
    body: ReturnCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.return:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ReturnResponse]:
    row = ReturnService(db).create(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Return created", data=ReturnResponse.model_validate(row))


@returns_router.get("/{return_id}", response_model=APIResponse[ReturnResponse])
def get_return(
    return_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.return:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ReturnResponse]:
    row = ReturnService(db).get_return(ctx, return_id)
    return APIResponse(message="Return retrieved", data=ReturnResponse.model_validate(row))


@returns_router.post("/{return_id}/lines", response_model=APIResponse[ReturnLineResponse])
def add_return_line(
    return_id: UUID,
    body: ReturnLineCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.return:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ReturnLineResponse]:
    line = ReturnService(db).add_line(ctx, return_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Return line added", data=ReturnLineResponse.model_validate(line))


@returns_router.post("/{return_id}/submit", response_model=APIResponse[ReturnResponse])
def submit_return(
    return_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.return:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ReturnResponse]:
    row = ReturnService(db).submit(ctx, return_id)
    db.commit()
    return APIResponse(message="Return submitted", data=ReturnResponse.model_validate(row))


@returns_router.post("/{return_id}/approve", response_model=APIResponse[dict])
def approve_return(
    return_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.return:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = ReturnService(db).approve(ctx, return_id)
    db.commit()
    return APIResponse(message="Return approved", data={"status": instance.status})


@returns_router.post("/{return_id}/receive", response_model=APIResponse[ReturnResponse])
def receive_return(
    return_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.return:receive"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ReturnResponse]:
    row = ReturnService(db).receive(ctx, return_id)
    db.commit()
    return APIResponse(message="Return received", data=ReturnResponse.model_validate(row))


@returns_router.post("/{return_id}/post", response_model=APIResponse[ReturnResponse])
def post_return(
    return_id: UUID,
    body: ReturnPostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.return:post"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ReturnResponse]:
    row = ProcurementPostingService(db).post_return(
        ctx,
        return_id,
        ap_account_id=body.ap_account_id,
        expense_account_id=body.expense_account_id,
    )
    db.commit()
    return APIResponse(message="Return posted", data=ReturnResponse.model_validate(row))
