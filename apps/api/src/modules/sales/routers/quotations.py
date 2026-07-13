"""Quotation routers."""

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
    QuotationCreateRequest,
    QuotationLineCreateRequest,
    QuotationLineResponse,
    QuotationResponse,
    QuotationUpdateRequest,
    SalesOrderResponse,
    WorkflowActionRequest,
)
from modules.sales.service.quotation_service import QuotationService
from shared.schemas import APIResponse

quotations_router = APIRouter(prefix="/quotations", tags=["Sales - Quotations"])


@quotations_router.get("", response_model=APIResponse[list[QuotationResponse]])
def list_quotations(
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[QuotationResponse]]:
    rows = QuotationService(db).list_quotations(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Quotations retrieved",
        data=[QuotationResponse.model_validate(r) for r in page],
    )


@quotations_router.post("", response_model=APIResponse[QuotationResponse])
def create_quotation(
    body: QuotationCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[QuotationResponse]:
    row = QuotationService(db).create(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Quotation created", data=QuotationResponse.model_validate(row))


@quotations_router.get("/{quotation_id}", response_model=APIResponse[QuotationResponse])
def get_quotation(
    quotation_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[QuotationResponse]:
    row = QuotationService(db).get_quotation(ctx, quotation_id)
    return APIResponse(message="Quotation retrieved", data=QuotationResponse.model_validate(row))


@quotations_router.patch("/{quotation_id}", response_model=APIResponse[QuotationResponse])
def update_quotation(
    quotation_id: UUID,
    body: QuotationUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[QuotationResponse]:
    row = QuotationService(db).update(ctx, quotation_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Quotation updated", data=QuotationResponse.model_validate(row))


@quotations_router.delete("/{quotation_id}", response_model=APIResponse[dict])
def delete_quotation(
    quotation_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    QuotationService(db).delete(ctx, quotation_id)
    db.commit()
    return APIResponse(message="Quotation deleted", data={})


@quotations_router.post(
    "/{quotation_id}/lines", response_model=APIResponse[QuotationLineResponse]
)
def add_quotation_line(
    quotation_id: UUID,
    body: QuotationLineCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[QuotationLineResponse]:
    line = QuotationService(db).add_line(ctx, quotation_id, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Quotation line added",
        data=QuotationLineResponse.model_validate(line),
    )


@quotations_router.post("/{quotation_id}/submit", response_model=APIResponse[QuotationResponse])
def submit_quotation(
    quotation_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[QuotationResponse]:
    row = QuotationService(db).submit(ctx, quotation_id)
    db.commit()
    return APIResponse(message="Quotation submitted", data=QuotationResponse.model_validate(row))


@quotations_router.post("/{quotation_id}/approve", response_model=APIResponse[dict])
def approve_quotation(
    quotation_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = QuotationService(db).approve(ctx, quotation_id)
    db.commit()
    return APIResponse(message="Quotation approved", data={"status": instance.status})


@quotations_router.post("/{quotation_id}/reject", response_model=APIResponse[dict])
def reject_quotation(
    quotation_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:reject"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = QuotationService(db).reject(ctx, quotation_id)
    db.commit()
    return APIResponse(message="Quotation rejected", data={"status": instance.status})


@quotations_router.post(
    "/{quotation_id}/convert", response_model=APIResponse[SalesOrderResponse]
)
def convert_quotation(
    quotation_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.quotation:convert"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[SalesOrderResponse]:
    order = QuotationService(db).convert_to_order(ctx, quotation_id)
    db.commit()
    return APIResponse(
        message="Quotation converted to order", data=SalesOrderResponse.model_validate(order)
    )
