"""UOM router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.dependencies import (
    PaginationParams,
    extract_update_fields,
    get_pagination,
    paginate,
)
from modules.master_data.schemas import UomCreateRequest, UomResponse, UomUpdateRequest
from modules.master_data.service.uom_service import UomService
from shared.schemas import APIResponse

router = APIRouter(prefix="/uoms", tags=["Master Data - UOMs"])


@router.get("", response_model=APIResponse[list[UomResponse]])
def list_uoms(
    ctx: Annotated[TenantContext, Depends(require_permission("master.uom:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[UomResponse]]:
    uoms = UomService(db).list_uoms(ctx, company_id=company_id)
    page = paginate(uoms, pagination)
    return APIResponse(
        message="UOMs retrieved",
        data=[UomResponse(**u.__dict__) for u in page],
    )


@router.post("", response_model=APIResponse[UomResponse])
def create_uom(
    body: UomCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.uom:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[UomResponse]:
    uom = UomService(db).create_uom(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="UOM created", data=UomResponse(**uom.__dict__))


@router.get("/{uom_id}", response_model=APIResponse[UomResponse])
def get_uom(
    uom_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.uom:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[UomResponse]:
    uom = UomService(db).get_uom(ctx, uom_id)
    return APIResponse(message="UOM retrieved", data=UomResponse(**uom.__dict__))


@router.put("/{uom_id}", response_model=APIResponse[UomResponse])
def update_uom(
    uom_id: UUID,
    body: UomUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.uom:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[UomResponse]:
    uom = UomService(db).update_uom(ctx, uom_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="UOM updated", data=UomResponse(**uom.__dict__))


@router.delete("/{uom_id}", response_model=APIResponse[None])
def delete_uom(
    uom_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.uom:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    UomService(db).delete_uom(ctx, uom_id)
    db.commit()
    return APIResponse(message="UOM deleted", data=None)
