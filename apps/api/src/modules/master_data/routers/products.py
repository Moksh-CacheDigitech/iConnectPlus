"""Product router."""

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
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
    SubmitApprovalRequest,
    WorkflowInstanceResponse,
)
from modules.master_data.service.product_service import ProductService
from shared.schemas import APIResponse

router = APIRouter(prefix="/products", tags=["Master Data - Products"])


@router.get("", response_model=APIResponse[list[ProductResponse]])
def list_products(
    ctx: Annotated[TenantContext, Depends(require_permission("master.product:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    branch_id: UUID | None = None,
) -> APIResponse[list[ProductResponse]]:
    products = ProductService(db).list_products(ctx, company_id=company_id, branch_id=branch_id)
    page = paginate(products, pagination)
    return APIResponse(
        message="Products retrieved",
        data=[ProductResponse(**p.__dict__) for p in page],
    )


@router.post("", response_model=APIResponse[ProductResponse])
def create_product(
    body: ProductCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ProductResponse]:
    product = ProductService(db).create_product(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Product created", data=ProductResponse(**product.__dict__))


@router.get("/{product_id}", response_model=APIResponse[ProductResponse])
def get_product(
    product_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ProductResponse]:
    product = ProductService(db).get_product(ctx, product_id)
    return APIResponse(message="Product retrieved", data=ProductResponse(**product.__dict__))


@router.put("/{product_id}", response_model=APIResponse[ProductResponse])
def update_product(
    product_id: UUID,
    body: ProductUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ProductResponse]:
    product = ProductService(db).update_product(ctx, product_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Product updated", data=ProductResponse(**product.__dict__))


@router.delete("/{product_id}", response_model=APIResponse[None])
def delete_product(
    product_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    ProductService(db).delete_product(ctx, product_id)
    db.commit()
    return APIResponse(message="Product deleted", data=None)


@router.post("/{product_id}/submit", response_model=APIResponse[WorkflowInstanceResponse])
def submit_product(
    product_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product:update"))],
    db: Annotated[Session, Depends(get_db)],
    body: SubmitApprovalRequest | None = None,
) -> APIResponse[WorkflowInstanceResponse]:
    _ = body
    instance = ProductService(db).submit_for_approval(ctx, product_id)
    db.commit()
    return APIResponse(
        message="Product submitted for approval",
        data=WorkflowInstanceResponse(**instance.__dict__),
    )
