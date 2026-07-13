"""Employee router."""

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
    EmployeeCreateRequest,
    EmployeeResponse,
    EmployeeUpdateRequest,
    SubmitApprovalRequest,
    WorkflowInstanceResponse,
)
from modules.master_data.service.employee_service import EmployeeService
from shared.schemas import APIResponse

router = APIRouter(prefix="/employees", tags=["Master Data - Employees"])


@router.get("", response_model=APIResponse[list[EmployeeResponse]])
def list_employees(
    ctx: Annotated[TenantContext, Depends(require_permission("master.employee:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    branch_id: UUID | None = None,
) -> APIResponse[list[EmployeeResponse]]:
    employees = EmployeeService(db).list_employees(ctx, company_id=company_id, branch_id=branch_id)
    page = paginate(employees, pagination)
    return APIResponse(
        message="Employees retrieved",
        data=[EmployeeResponse(**e.__dict__) for e in page],
    )


@router.post("", response_model=APIResponse[EmployeeResponse])
def create_employee(
    body: EmployeeCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.employee:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[EmployeeResponse]:
    employee = EmployeeService(db).create_employee(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Employee created", data=EmployeeResponse(**employee.__dict__))


@router.get("/{employee_id}", response_model=APIResponse[EmployeeResponse])
def get_employee(
    employee_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.employee:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[EmployeeResponse]:
    employee = EmployeeService(db).get_employee(ctx, employee_id)
    return APIResponse(message="Employee retrieved", data=EmployeeResponse(**employee.__dict__))


@router.put("/{employee_id}", response_model=APIResponse[EmployeeResponse])
def update_employee(
    employee_id: UUID,
    body: EmployeeUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("master.employee:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[EmployeeResponse]:
    employee = EmployeeService(db).update_employee(ctx, employee_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Employee updated", data=EmployeeResponse(**employee.__dict__))


@router.delete("/{employee_id}", response_model=APIResponse[None])
def delete_employee(
    employee_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.employee:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    EmployeeService(db).delete_employee(ctx, employee_id)
    db.commit()
    return APIResponse(message="Employee deleted", data=None)


@router.post("/{employee_id}/submit", response_model=APIResponse[WorkflowInstanceResponse])
def submit_employee(
    employee_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("master.employee:update"))],
    db: Annotated[Session, Depends(get_db)],
    body: SubmitApprovalRequest | None = None,
) -> APIResponse[WorkflowInstanceResponse]:
    _ = body
    instance = EmployeeService(db).submit_for_approval(ctx, employee_id)
    db.commit()
    return APIResponse(
        message="Employee submitted for approval",
        data=WorkflowInstanceResponse(**instance.__dict__),
    )
