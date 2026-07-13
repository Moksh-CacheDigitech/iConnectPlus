"""Asset router."""

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
from modules.master_data.schemas import AssetCreateRequest, AssetResponse, AssetUpdateRequest
from modules.master_data.service.asset_service import AssetService
from shared.schemas import APIResponse

router = APIRouter(prefix="/assets", tags=["Master Data - Assets"])


@router.get("", response_model=APIResponse[list[AssetResponse]])
def list_assets(
    ctx: Annotated[TenantContext, Depends(require_permission("master.asset:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    branch_id: UUID | None = None,
) -> APIResponse[list[AssetResponse]]:
    assets = AssetService(db).list_assets(ctx, company_id=company_id, branch_id=branch_id)
    page = paginate(assets, pagination)
    return APIResponse(
        message="Assets retrieved",
        data=[AssetResponse(**a.__dict__) for a in page],
    )


@router.post("", response_model=APIResponse[AssetResponse])
def create_asset(
    body: AssetCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.asset:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[AssetResponse]:
    asset = AssetService(db).create_asset(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Asset created", data=AssetResponse(**asset.__dict__))


@router.get("/{asset_id}", response_model=APIResponse[AssetResponse])
def get_asset(
    asset_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.asset:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[AssetResponse]:
    asset = AssetService(db).get_asset(ctx, asset_id)
    return APIResponse(message="Asset retrieved", data=AssetResponse(**asset.__dict__))


@router.put("/{asset_id}", response_model=APIResponse[AssetResponse])
def update_asset(
    asset_id: UUID,
    body: AssetUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.asset:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[AssetResponse]:
    asset = AssetService(db).update_asset(ctx, asset_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Asset updated", data=AssetResponse(**asset.__dict__))


@router.delete("/{asset_id}", response_model=APIResponse[None])
def delete_asset(
    asset_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.asset:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    AssetService(db).delete_asset(ctx, asset_id)
    db.commit()
    return APIResponse(message="Asset deleted", data=None)
