"""Procurement requisition routers."""

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
    RequisitionCreateRequest,
    RequisitionLineCreateRequest,
    RequisitionLineResponse,
    RequisitionResponse,
    RequisitionUpdateRequest,
    RfqResponse,
    WorkflowActionRequest,
)
from modules.procurement.service.requisition_service import RequisitionService
from shared.schemas import APIResponse

requisitions_router = APIRouter(prefix="/requisitions", tags=["Procurement - Requisitions"])


@requisitions_router.get("", response_model=APIResponse[list[RequisitionResponse]])
def list_requisitions(
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[RequisitionResponse]]:
    rows = RequisitionService(db).list_requisitions(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Requisitions retrieved",
        data=[RequisitionResponse.model_validate(r) for r in page],
    )


@requisitions_router.post("", response_model=APIResponse[RequisitionResponse])
def create_requisition(
    body: RequisitionCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RequisitionResponse]:
    row = RequisitionService(db).create(ctx, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Requisition created", data=RequisitionResponse.model_validate(row)
    )


@requisitions_router.get("/{requisition_id}", response_model=APIResponse[RequisitionResponse])
def get_requisition(
    requisition_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RequisitionResponse]:
    row = RequisitionService(db).get_requisition(ctx, requisition_id)
    return APIResponse(
        message="Requisition retrieved", data=RequisitionResponse.model_validate(row)
    )


@requisitions_router.patch("/{requisition_id}", response_model=APIResponse[RequisitionResponse])
def update_requisition(
    requisition_id: UUID,
    body: RequisitionUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RequisitionResponse]:
    row = RequisitionService(db).update(ctx, requisition_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(
        message="Requisition updated", data=RequisitionResponse.model_validate(row)
    )


@requisitions_router.delete("/{requisition_id}", response_model=APIResponse[dict])
def delete_requisition(
    requisition_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    RequisitionService(db).delete(ctx, requisition_id)
    db.commit()
    return APIResponse(message="Requisition deleted", data={})


@requisitions_router.post(
    "/{requisition_id}/lines", response_model=APIResponse[RequisitionLineResponse]
)
def add_requisition_line(
    requisition_id: UUID,
    body: RequisitionLineCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RequisitionLineResponse]:
    line = RequisitionService(db).add_line(ctx, requisition_id, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Requisition line added",
        data=RequisitionLineResponse.model_validate(line),
    )


@requisitions_router.post(
    "/{requisition_id}/submit",
    response_model=APIResponse[RequisitionResponse],
)
def submit_requisition(
    requisition_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RequisitionResponse]:
    row = RequisitionService(db).submit(ctx, requisition_id)
    db.commit()
    return APIResponse(
        message="Requisition submitted", data=RequisitionResponse.model_validate(row)
    )


@requisitions_router.post("/{requisition_id}/approve", response_model=APIResponse[dict])
def approve_requisition(
    requisition_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = RequisitionService(db).approve(ctx, requisition_id)
    db.commit()
    return APIResponse(message="Requisition approved", data={"status": instance.status})


@requisitions_router.post("/{requisition_id}/convert", response_model=APIResponse[RfqResponse])
def convert_requisition(
    requisition_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.requisition:convert"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[RfqResponse]:
    rfq = RequisitionService(db).convert_to_rfq(ctx, requisition_id)
    db.commit()
    return APIResponse(
        message="Requisition converted to RFQ", data=RfqResponse.model_validate(rfq)
    )
