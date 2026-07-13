"""Customer router."""

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
from modules.master_data.schemas import (
    CustomerCreateRequest,
    CustomerResponse,
    CustomerUpdateRequest,
    SubmitApprovalRequest,
    WorkflowInstanceResponse,
)
from modules.master_data.service.customer_service import CustomerService
from shared.schemas import APIResponse

router = APIRouter(prefix="/customers", tags=["Master Data - Customers"])


@router.get("", response_model=APIResponse[list[CustomerResponse]])
def list_customers(
    ctx: Annotated[TenantContext, Depends(require_permission("master.customer:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    branch_id: UUID | None = None,
) -> APIResponse[list[CustomerResponse]]:
    customers = CustomerService(db).list_customers(ctx, company_id=company_id, branch_id=branch_id)
    page = paginate(customers, pagination)
    return APIResponse(
        message="Customers retrieved",
        data=[CustomerResponse(**c.__dict__) for c in page],
    )


@router.post("", response_model=APIResponse[CustomerResponse])
def create_customer(
    body: CustomerCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.customer:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CustomerResponse]:
    customer = CustomerService(db).create_customer(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Customer created", data=CustomerResponse(**customer.__dict__))


@router.get("/{customer_id}", response_model=APIResponse[CustomerResponse])
def get_customer(
    customer_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.customer:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CustomerResponse]:
    customer = CustomerService(db).get_customer(ctx, customer_id)
    return APIResponse(message="Customer retrieved", data=CustomerResponse(**customer.__dict__))


@router.put("/{customer_id}", response_model=APIResponse[CustomerResponse])
def update_customer(
    customer_id: UUID,
    body: CustomerUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.customer:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CustomerResponse]:
    customer = CustomerService(db).update_customer(ctx, customer_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Customer updated", data=CustomerResponse(**customer.__dict__))


@router.post("/{customer_id}/submit", response_model=APIResponse[WorkflowInstanceResponse])
def submit_customer(
    customer_id: UUID,
    _body: SubmitApprovalRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.customer:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[WorkflowInstanceResponse]:
    instance = CustomerService(db).submit_for_approval(ctx, customer_id)
    db.commit()
    return APIResponse(
        message="Customer submitted for approval",
        data=WorkflowInstanceResponse(**instance.__dict__),
    )


@router.delete("/{customer_id}", response_model=APIResponse[None])
def delete_customer(
    customer_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.customer:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    CustomerService(db).delete_customer(ctx, customer_id)
    db.commit()
    return APIResponse(message="Customer deleted", data=None)
