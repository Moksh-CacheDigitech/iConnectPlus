"""Tax router."""

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
from modules.master_data.schemas import TaxCreateRequest, TaxResponse, TaxUpdateRequest
from modules.master_data.service.tax_service import TaxService
from shared.schemas import APIResponse

router = APIRouter(prefix="/taxes", tags=["Master Data - Taxes"])


@router.get("", response_model=APIResponse[list[TaxResponse]])
def list_taxes(
    ctx: Annotated[TenantContext, Depends(require_permission("master.tax:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[TaxResponse]]:
    taxes = TaxService(db).list_taxes(ctx, company_id=company_id)
    page = paginate(taxes, pagination)
    return APIResponse(
        message="Taxes retrieved",
        data=[TaxResponse(**t.__dict__) for t in page],
    )


@router.post("", response_model=APIResponse[TaxResponse])
def create_tax(
    body: TaxCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.tax:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[TaxResponse]:
    tax = TaxService(db).create_tax(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Tax created", data=TaxResponse(**tax.__dict__))


@router.get("/{tax_id}", response_model=APIResponse[TaxResponse])
def get_tax(
    tax_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.tax:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[TaxResponse]:
    tax = TaxService(db).get_tax(ctx, tax_id)
    return APIResponse(message="Tax retrieved", data=TaxResponse(**tax.__dict__))


@router.put("/{tax_id}", response_model=APIResponse[TaxResponse])
def update_tax(
    tax_id: UUID,
    body: TaxUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.tax:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[TaxResponse]:
    tax = TaxService(db).update_tax(ctx, tax_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Tax updated", data=TaxResponse(**tax.__dict__))


@router.delete("/{tax_id}", response_model=APIResponse[None])
def delete_tax(
    tax_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.tax:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    TaxService(db).delete_tax(ctx, tax_id)
    db.commit()
    return APIResponse(message="Tax deleted", data=None)
