"""Currency router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.master_data.dependencies import (
    PaginationParams,
    extract_update_fields,
    get_pagination,
    paginate,
)
from modules.master_data.schemas import (
    CurrencyCreateRequest,
    CurrencyResponse,
    CurrencyUpdateRequest,
)
from modules.master_data.service.currency_service import CurrencyService
from shared.schemas import APIResponse

router = APIRouter(prefix="/currencies", tags=["Master Data - Currencies"])


@router.get("", response_model=APIResponse[list[CurrencyResponse]])
def list_currencies(
    ctx: Annotated[TenantContext, Depends(require_permission("master.currency:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[CurrencyResponse]]:
    currencies = CurrencyService(db).list_currencies(ctx, company_id=company_id)
    page = paginate(currencies, pagination)
    return APIResponse(
        message="Currencies retrieved",
        data=[CurrencyResponse(**c.__dict__) for c in page],
    )


@router.get("/base", response_model=APIResponse[CurrencyResponse])
def get_base_currency(
    ctx: Annotated[TenantContext, Depends(require_permission("master.currency:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[CurrencyResponse]:
    currencies = CurrencyService(db).list_currencies(ctx, company_id=company_id)
    base = next((currency for currency in currencies if currency.is_base_currency), None)
    if base is None:
        raise NotFoundException("Base currency not found")
    return APIResponse(message="Base currency retrieved", data=CurrencyResponse(**base.__dict__))


@router.post("", response_model=APIResponse[CurrencyResponse])
def create_currency(
    body: CurrencyCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.currency:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CurrencyResponse]:
    currency = CurrencyService(db).create_currency(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Currency created", data=CurrencyResponse(**currency.__dict__))


@router.get("/{currency_id}", response_model=APIResponse[CurrencyResponse])
def get_currency(
    currency_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.currency:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CurrencyResponse]:
    currency = CurrencyService(db).get_currency(ctx, currency_id)
    return APIResponse(message="Currency retrieved", data=CurrencyResponse(**currency.__dict__))


@router.put("/{currency_id}", response_model=APIResponse[CurrencyResponse])
def update_currency(
    currency_id: UUID,
    body: CurrencyUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.currency:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CurrencyResponse]:
    currency = CurrencyService(db).update_currency(ctx, currency_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Currency updated", data=CurrencyResponse(**currency.__dict__))


@router.delete("/{currency_id}", response_model=APIResponse[None])
def delete_currency(
    currency_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.currency:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    CurrencyService(db).delete_currency(ctx, currency_id)
    db.commit()
    return APIResponse(message="Currency deleted", data=None)
