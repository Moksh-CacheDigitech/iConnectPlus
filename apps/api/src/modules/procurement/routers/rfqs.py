"""Procurement RFQ routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.dependencies import (
    PaginationParams,
    extract_update_fields,
    get_pagination,
    paginate,
)
from modules.procurement.schemas import (
    RfqCreateRequest,
    RfqLineCreateRequest,
    RfqLineResponse,
    RfqResponse,
    RfqUpdateRequest,
    RfqVendorCreateRequest,
    RfqVendorResponse,
    WorkflowActionRequest,
)
from modules.procurement.service.rfq_service import RfqService
from shared.schemas import APIResponse

rfqs_router = APIRouter(prefix="/rfqs", tags=["Procurement - RFQs"])


@rfqs_router.get("", response_model=APIResponse[list[RfqResponse]])
def list_rfqs(
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.rfq:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[RfqResponse]]:
    rows = RfqService(db).list_rfqs(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="RFQs retrieved",
        data=[RfqResponse.model_validate(r) for r in page],
    )


@rfqs_router.post("", response_model=APIResponse[RfqResponse])
def create_rfq(
    body: RfqCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.rfq:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RfqResponse]:
    row = RfqService(db).create(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="RFQ created", data=RfqResponse.model_validate(row))


@rfqs_router.get("/{rfq_id}", response_model=APIResponse[RfqResponse])
def get_rfq(
    rfq_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.rfq:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RfqResponse]:
    row = RfqService(db).get_rfq(ctx, rfq_id)
    return APIResponse(message="RFQ retrieved", data=RfqResponse.model_validate(row))


@rfqs_router.patch("/{rfq_id}", response_model=APIResponse[RfqResponse])
def update_rfq(
    rfq_id: UUID,
    body: RfqUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.rfq:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RfqResponse]:
    row = RfqService(db).update(ctx, rfq_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="RFQ updated", data=RfqResponse.model_validate(row))


@rfqs_router.post("/{rfq_id}/lines", response_model=APIResponse[RfqLineResponse])
def add_rfq_line(
    rfq_id: UUID,
    body: RfqLineCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.rfq:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RfqLineResponse]:
    line = RfqService(db).add_line(ctx, rfq_id, **body.model_dump())
    db.commit()
    return APIResponse(message="RFQ line added", data=RfqLineResponse.model_validate(line))


@rfqs_router.post("/{rfq_id}/vendors", response_model=APIResponse[RfqVendorResponse])
def add_rfq_vendor(
    rfq_id: UUID,
    body: RfqVendorCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.rfq:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RfqVendorResponse]:
    vendor = RfqService(db).add_vendor(ctx, rfq_id, **body.model_dump())
    db.commit()
    return APIResponse(message="RFQ vendor invited", data=RfqVendorResponse.model_validate(vendor))


@rfqs_router.post("/{rfq_id}/publish", response_model=APIResponse[RfqResponse])
def publish_rfq(
    rfq_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.rfq:publish"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RfqResponse]:
    row = RfqService(db).publish(ctx, rfq_id)
    db.commit()
    return APIResponse(message="RFQ published", data=RfqResponse.model_validate(row))


@rfqs_router.post("/{rfq_id}/close", response_model=APIResponse[RfqResponse])
def close_rfq(
    rfq_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.rfq:close"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RfqResponse]:
    row = RfqService(db).close(ctx, rfq_id)
    db.commit()
    return APIResponse(message="RFQ closed", data=RfqResponse.model_validate(row))
