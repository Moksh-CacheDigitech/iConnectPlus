"""Warehouse router."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
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
    WarehouseCreateRequest,
    WarehouseResponse,
    WarehouseUpdateRequest,
)
from modules.master_data.service.warehouse_service import WarehouseService
from shared.schemas import APIResponse

router = APIRouter(prefix="/warehouses", tags=["Master Data - Warehouses"])


@router.get("", response_model=APIResponse[list[WarehouseResponse]])
def list_warehouses(
    ctx: Annotated[TenantContext, Depends(require_permission("master.warehouse:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    branch_id: UUID | None = None,
) -> APIResponse[list[WarehouseResponse]]:
    warehouses = WarehouseService(db).list_warehouses(
        ctx, company_id=company_id, branch_id=branch_id
    )
    page = paginate(warehouses, pagination)
    return APIResponse(
        message="Warehouses retrieved",
        data=[WarehouseResponse(**w.__dict__) for w in page],
    )


@router.get("/default", response_model=APIResponse[WarehouseResponse])
def get_default_warehouse(
    ctx: Annotated[TenantContext, Depends(require_permission("master.warehouse:read"))],
    db: Annotated[Session, Depends(get_db)],
    branch_id: Annotated[UUID, Query()],
) -> APIResponse[WarehouseResponse]:
    warehouses = WarehouseService(db).list_warehouses(ctx, branch_id=branch_id)
    default = next((warehouse for warehouse in warehouses if warehouse.is_default), None)
    if default is None:
        raise NotFoundException("Default warehouse not found")
    return APIResponse(
        message="Default warehouse retrieved", data=WarehouseResponse(**default.__dict__)
    )


@router.post("", response_model=APIResponse[WarehouseResponse])
def create_warehouse(
    body: WarehouseCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.warehouse:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[WarehouseResponse]:
    warehouse = WarehouseService(db).create_warehouse(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Warehouse created", data=WarehouseResponse(**warehouse.__dict__))


@router.get("/{warehouse_id}", response_model=APIResponse[WarehouseResponse])
def get_warehouse(
    warehouse_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.warehouse:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[WarehouseResponse]:
    warehouse = WarehouseService(db).get_warehouse(ctx, warehouse_id)
    return APIResponse(message="Warehouse retrieved", data=WarehouseResponse(**warehouse.__dict__))


@router.put("/{warehouse_id}", response_model=APIResponse[WarehouseResponse])
def update_warehouse(
    warehouse_id: UUID,
    body: WarehouseUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.warehouse:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[WarehouseResponse]:
    warehouse = WarehouseService(db).update_warehouse(
        ctx, warehouse_id, **extract_update_fields(body)
    )
    db.commit()
    return APIResponse(message="Warehouse updated", data=WarehouseResponse(**warehouse.__dict__))


@router.delete("/{warehouse_id}", response_model=APIResponse[None])
def delete_warehouse(
    warehouse_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.warehouse:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    WarehouseService(db).delete_warehouse(ctx, warehouse_id)
    db.commit()
    return APIResponse(message="Warehouse deleted", data=None)
