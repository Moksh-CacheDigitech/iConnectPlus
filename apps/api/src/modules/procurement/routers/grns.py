"""Procurement GRN routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.dependencies import PaginationParams, get_pagination, paginate
from modules.procurement.schemas import GrnCreateRequest, GrnResponse
from modules.procurement.service.grn_service import GrnService
from shared.schemas import APIResponse

grns_router = APIRouter(prefix="/grns", tags=["Procurement - GRNs"])


@grns_router.get("", response_model=APIResponse[list[GrnResponse]])
def list_grns(
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.grn:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[GrnResponse]]:
    rows = GrnService(db).list_grns(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="GRNs retrieved",
        data=[GrnResponse.model_validate(r) for r in page],
    )


@grns_router.post("", response_model=APIResponse[GrnResponse])
def create_grn(
    body: GrnCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.grn:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[GrnResponse]:
    row = GrnService(db).create_from_order(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="GRN created", data=GrnResponse.model_validate(row))


@grns_router.get("/{grn_id}", response_model=APIResponse[GrnResponse])
def get_grn(
    grn_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.grn:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[GrnResponse]:
    row = GrnService(db).get_grn(ctx, grn_id)
    return APIResponse(message="GRN retrieved", data=GrnResponse.model_validate(row))


@grns_router.post("/{grn_id}/confirm", response_model=APIResponse[GrnResponse])
def confirm_grn(
    grn_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.grn:confirm"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[GrnResponse]:
    row = GrnService(db).confirm(ctx, grn_id)
    db.commit()
    return APIResponse(message="GRN confirmed", data=GrnResponse.model_validate(row))
