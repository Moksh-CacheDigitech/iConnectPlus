"""Finance COA routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.finance.dependencies import PaginationParams, get_pagination, paginate
from modules.finance.schemas import (
    AccountGroupCreateRequest,
    AccountGroupResponse,
    ChartOfAccountCreateRequest,
    ChartOfAccountResponse,
)
from modules.finance.service.chart_of_account_service import ChartOfAccountService
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from shared.schemas import APIResponse

account_groups_router = APIRouter(prefix="/account-groups", tags=["Finance - Account Groups"])
chart_of_accounts_router = APIRouter(prefix="/chart-of-accounts", tags=["Finance - COA"])


@account_groups_router.get("", response_model=APIResponse[list[AccountGroupResponse]])
def list_account_groups(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.coa:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[list[AccountGroupResponse]]:
    groups = ChartOfAccountService(db).list_account_groups(ctx, company_id)
    return APIResponse(message="Account groups retrieved", data=[AccountGroupResponse.model_validate(g) for g in groups])


@account_groups_router.post("", response_model=APIResponse[AccountGroupResponse])
def create_account_group(
    body: AccountGroupCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.coa:create"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[AccountGroupResponse]:
    group = ChartOfAccountService(db).create_account_group(ctx, company_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Account group created", data=AccountGroupResponse.model_validate(group))


@chart_of_accounts_router.get("", response_model=APIResponse[list[ChartOfAccountResponse]])
def list_accounts(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.coa:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[ChartOfAccountResponse]]:
    accounts = ChartOfAccountService(db).list_accounts(ctx, company_id)
    page = paginate(accounts, pagination)
    return APIResponse(
        message="Chart of accounts retrieved",
        data=[ChartOfAccountResponse.model_validate(a) for a in page],
    )


@chart_of_accounts_router.post("", response_model=APIResponse[ChartOfAccountResponse])
def create_account(
    body: ChartOfAccountCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.coa:create"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[ChartOfAccountResponse]:
    account = ChartOfAccountService(db).create_account(ctx, company_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Account created", data=ChartOfAccountResponse.model_validate(account))
