"""Customer credit routers."""

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
    CustomerCreditCreateRequest,
    CustomerCreditResponse,
    CustomerCreditUpdateRequest,
)
from modules.sales.service.customer_credit_service import CustomerCreditService
from shared.schemas import APIResponse

customer_credit_router = APIRouter(prefix="/customer-credit", tags=["Sales - Customer Credit"])


@customer_credit_router.get("", response_model=APIResponse[list[CustomerCreditResponse]])
def list_customer_credits(
    ctx: Annotated[TenantContext, Depends(require_permission("sales.customer_credit:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[CustomerCreditResponse]]:
    rows = CustomerCreditService(db).list_credits(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Customer credits retrieved",
        data=[CustomerCreditResponse.model_validate(r) for r in page],
    )


@customer_credit_router.post("", response_model=APIResponse[CustomerCreditResponse])
def create_customer_credit(
    body: CustomerCreditCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.customer_credit:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CustomerCreditResponse]:
    row = CustomerCreditService(db).create_credit(ctx, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Customer credit created", data=CustomerCreditResponse.model_validate(row)
    )


@customer_credit_router.get("/{credit_id}", response_model=APIResponse[CustomerCreditResponse])
def get_customer_credit(
    credit_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.customer_credit:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CustomerCreditResponse]:
    row = CustomerCreditService(db).get_credit(ctx, credit_id)
    return APIResponse(
        message="Customer credit retrieved", data=CustomerCreditResponse.model_validate(row)
    )


@customer_credit_router.patch("/{credit_id}", response_model=APIResponse[CustomerCreditResponse])
def update_customer_credit(
    credit_id: UUID,
    body: CustomerCreditUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.customer_credit:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CustomerCreditResponse]:
    row = CustomerCreditService(db).update_credit(ctx, credit_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(
        message="Customer credit updated", data=CustomerCreditResponse.model_validate(row)
    )
