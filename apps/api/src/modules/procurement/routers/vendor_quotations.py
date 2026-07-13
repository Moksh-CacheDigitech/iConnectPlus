"""Procurement vendor quotation routers."""

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
    VendorQuotationCreateRequest,
    VendorQuotationLineCreateRequest,
    VendorQuotationLineResponse,
    VendorQuotationResponse,
    VendorQuotationSelectRequest,
    VendorQuotationUpdateRequest,
)
from modules.procurement.service.vendor_quotation_service import VendorQuotationService
from shared.schemas import APIResponse

vendor_quotations_router = APIRouter(
    prefix="/vendor-quotations", tags=["Procurement - Vendor Quotations"]
)


@vendor_quotations_router.get("", response_model=APIResponse[list[VendorQuotationResponse]])
def list_vendor_quotations(
    ctx: Annotated[
        TenantContext, Depends(require_permission("procurement.vendor_quotation:read"))
    ],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[VendorQuotationResponse]]:
    rows = VendorQuotationService(db).list_quotations(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Vendor quotations retrieved",
        data=[VendorQuotationResponse.model_validate(r) for r in page],
    )


@vendor_quotations_router.post("", response_model=APIResponse[VendorQuotationResponse])
def create_vendor_quotation(
    body: VendorQuotationCreateRequest,
    ctx: Annotated[
        TenantContext, Depends(require_permission("procurement.vendor_quotation:create"))
    ],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[VendorQuotationResponse]:
    row = VendorQuotationService(db).create(ctx, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Vendor quotation created", data=VendorQuotationResponse.model_validate(row)
    )


@vendor_quotations_router.get(
    "/{quotation_id}", response_model=APIResponse[VendorQuotationResponse]
)
def get_vendor_quotation(
    quotation_id: UUID,
    ctx: Annotated[
        TenantContext, Depends(require_permission("procurement.vendor_quotation:read"))
    ],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[VendorQuotationResponse]:
    row = VendorQuotationService(db).get_quotation(ctx, quotation_id)
    return APIResponse(
        message="Vendor quotation retrieved",
        data=VendorQuotationResponse.model_validate(row),
    )


@vendor_quotations_router.patch(
    "/{quotation_id}", response_model=APIResponse[VendorQuotationResponse]
)
def update_vendor_quotation(
    quotation_id: UUID,
    body: VendorQuotationUpdateRequest,
    ctx: Annotated[
        TenantContext, Depends(require_permission("procurement.vendor_quotation:update"))
    ],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[VendorQuotationResponse]:
    row = VendorQuotationService(db).update(
        ctx, quotation_id, **extract_update_fields(body)
    )
    db.commit()
    return APIResponse(
        message="Vendor quotation updated", data=VendorQuotationResponse.model_validate(row)
    )


@vendor_quotations_router.post(
    "/{quotation_id}/lines", response_model=APIResponse[VendorQuotationLineResponse]
)
def add_vendor_quotation_line(
    quotation_id: UUID,
    body: VendorQuotationLineCreateRequest,
    ctx: Annotated[
        TenantContext, Depends(require_permission("procurement.vendor_quotation:update"))
    ],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[VendorQuotationLineResponse]:
    line = VendorQuotationService(db).add_line(ctx, quotation_id, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Vendor quotation line added",
        data=VendorQuotationLineResponse.model_validate(line),
    )


@vendor_quotations_router.post(
    "/{quotation_id}/select", response_model=APIResponse[VendorQuotationResponse]
)
def select_vendor_quotation(
    quotation_id: UUID,
    _body: VendorQuotationSelectRequest,
    ctx: Annotated[
        TenantContext, Depends(require_permission("procurement.vendor_quotation:select"))
    ],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[VendorQuotationResponse]:
    row = VendorQuotationService(db).select(ctx, quotation_id)
    db.commit()
    return APIResponse(
        message="Vendor quotation selected", data=VendorQuotationResponse.model_validate(row)
    )
