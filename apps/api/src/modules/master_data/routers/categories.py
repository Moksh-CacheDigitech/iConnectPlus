"""Product category router."""

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
    CategoryCreateRequest,
    CategoryResponse,
    CategoryTreeNode,
    CategoryUpdateRequest,
)
from modules.master_data.service.category_service import CategoryService
from shared.schemas import APIResponse

router = APIRouter(prefix="/product-categories", tags=["Master Data - Categories"])


def _build_category_tree(categories) -> list[CategoryTreeNode]:
    nodes: dict[UUID, CategoryTreeNode] = {}
    for category in categories:
        nodes[category.id] = CategoryTreeNode(
            id=category.id,
            category_code=category.category_code,
            category_name=category.category_name,
            status=category.status,
            parent_category_id=category.parent_category_id,
            level=category.level,
            children=[],
        )

    roots: list[CategoryTreeNode] = []
    for category in categories:
        node = nodes[category.id]
        if category.parent_category_id and category.parent_category_id in nodes:
            nodes[category.parent_category_id].children.append(node)
        else:
            roots.append(node)
    return roots


@router.get("", response_model=APIResponse[list[CategoryResponse]])
def list_categories(
    ctx: Annotated[TenantContext, Depends(require_permission("master.product_category:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[CategoryResponse]]:
    categories = CategoryService(db).list_categories(ctx, company_id=company_id)
    page = paginate(categories, pagination)
    return APIResponse(
        message="Categories retrieved",
        data=[CategoryResponse(**c.__dict__) for c in page],
    )


@router.get("/tree", response_model=APIResponse[list[CategoryTreeNode]])
def get_category_tree(
    ctx: Annotated[TenantContext, Depends(require_permission("master.product_category:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[list[CategoryTreeNode]]:
    categories = CategoryService(db).list_categories(ctx, company_id=company_id)
    return APIResponse(message="Category tree retrieved", data=_build_category_tree(categories))


@router.post("", response_model=APIResponse[CategoryResponse])
def create_category(
    body: CategoryCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product_category:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CategoryResponse]:
    category = CategoryService(db).create_category(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Category created", data=CategoryResponse(**category.__dict__))


@router.get("/{category_id}", response_model=APIResponse[CategoryResponse])
def get_category(
    category_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product_category:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CategoryResponse]:
    category = CategoryService(db).get_category(ctx, category_id)
    return APIResponse(message="Category retrieved", data=CategoryResponse(**category.__dict__))


@router.put("/{category_id}", response_model=APIResponse[CategoryResponse])
def update_category(
    category_id: UUID,
    body: CategoryUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product_category:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CategoryResponse]:
    category = CategoryService(db).update_category(ctx, category_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Category updated", data=CategoryResponse(**category.__dict__))


@router.delete("/{category_id}", response_model=APIResponse[None])
def delete_category(
    category_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.product_category:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    CategoryService(db).delete_category(ctx, category_id)
    db.commit()
    return APIResponse(message="Category deleted", data=None)
