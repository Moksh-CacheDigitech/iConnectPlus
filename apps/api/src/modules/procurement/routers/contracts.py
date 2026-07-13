"""Procurement vendor contract routers."""

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
    ContractCreateRequest,
    ContractLineCreateRequest,
    ContractLineResponse,
    ContractResponse,
    ContractUpdateRequest,
    WorkflowActionRequest,
)
from modules.procurement.service.contract_service import ContractService
from shared.schemas import APIResponse

contracts_router = APIRouter(prefix="/contracts", tags=["Procurement - Contracts"])


@contracts_router.get("", response_model=APIResponse[list[ContractResponse]])
def list_contracts(
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.contract:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[ContractResponse]]:
    rows = ContractService(db).list_contracts(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Contracts retrieved",
        data=[ContractResponse.model_validate(r) for r in page],
    )


@contracts_router.post("", response_model=APIResponse[ContractResponse])
def create_contract(
    body: ContractCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.contract:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ContractResponse]:
    row = ContractService(db).create(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Contract created", data=ContractResponse.model_validate(row))


@contracts_router.get("/{contract_id}", response_model=APIResponse[ContractResponse])
def get_contract(
    contract_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.contract:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ContractResponse]:
    row = ContractService(db).get_contract(ctx, contract_id)
    return APIResponse(message="Contract retrieved", data=ContractResponse.model_validate(row))


@contracts_router.patch("/{contract_id}", response_model=APIResponse[ContractResponse])
def update_contract(
    contract_id: UUID,
    body: ContractUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.contract:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ContractResponse]:
    row = ContractService(db).update(ctx, contract_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Contract updated", data=ContractResponse.model_validate(row))


@contracts_router.post("/{contract_id}/lines", response_model=APIResponse[ContractLineResponse])
def add_contract_line(
    contract_id: UUID,
    body: ContractLineCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.contract:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ContractLineResponse]:
    line = ContractService(db).add_line(ctx, contract_id, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Contract line added",
        data=ContractLineResponse.model_validate(line),
    )


@contracts_router.post("/{contract_id}/submit", response_model=APIResponse[ContractResponse])
def submit_contract(
    contract_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.contract:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[ContractResponse]:
    row = ContractService(db).submit(ctx, contract_id)
    db.commit()
    return APIResponse(message="Contract submitted", data=ContractResponse.model_validate(row))


@contracts_router.post("/{contract_id}/approve", response_model=APIResponse[dict])
def approve_contract(
    contract_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.contract:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = ContractService(db).approve(ctx, contract_id)
    db.commit()
    return APIResponse(message="Contract approved", data={"status": instance.status})
