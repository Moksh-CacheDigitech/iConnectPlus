"""Discount rule routers."""

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
    DiscountRuleCreateRequest,
    DiscountRuleResponse,
    DiscountRuleUpdateRequest,
    WorkflowActionRequest,
)
from modules.sales.service.discount_service import DiscountService
from shared.schemas import APIResponse

discount_rules_router = APIRouter(prefix="/discount-rules", tags=["Sales - Discount Rules"])


@discount_rules_router.get("", response_model=APIResponse[list[DiscountRuleResponse]])
def list_discount_rules(
    ctx: Annotated[TenantContext, Depends(require_permission("sales.discount_rule:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[DiscountRuleResponse]]:
    rows = DiscountService(db).list_rules(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Discount rules retrieved",
        data=[DiscountRuleResponse.model_validate(r) for r in page],
    )


@discount_rules_router.post("", response_model=APIResponse[DiscountRuleResponse])
def create_discount_rule(
    body: DiscountRuleCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.discount_rule:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[DiscountRuleResponse]:
    row = DiscountService(db).create_rule(ctx, **body.model_dump())
    db.commit()
    return APIResponse(
        message="Discount rule created",
        data=DiscountRuleResponse.model_validate(row),
    )


@discount_rules_router.get("/{rule_id}", response_model=APIResponse[DiscountRuleResponse])
def get_discount_rule(
    rule_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.discount_rule:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[DiscountRuleResponse]:
    row = DiscountService(db).get_rule(ctx, rule_id)
    return APIResponse(
        message="Discount rule retrieved",
        data=DiscountRuleResponse.model_validate(row),
    )


@discount_rules_router.patch("/{rule_id}", response_model=APIResponse[DiscountRuleResponse])
def update_discount_rule(
    rule_id: UUID,
    body: DiscountRuleUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.discount_rule:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[DiscountRuleResponse]:
    row = DiscountService(db).update_rule(ctx, rule_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(
        message="Discount rule updated",
        data=DiscountRuleResponse.model_validate(row),
    )


@discount_rules_router.delete("/{rule_id}", response_model=APIResponse[dict])
def delete_discount_rule(
    rule_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.discount_rule:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    DiscountService(db).delete_rule(ctx, rule_id)
    db.commit()
    return APIResponse(message="Discount rule deleted", data={})


@discount_rules_router.post("/{rule_id}/submit", response_model=APIResponse[DiscountRuleResponse])
def submit_discount_rule(
    rule_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.discount_rule:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[DiscountRuleResponse]:
    row = DiscountService(db).submit(ctx, rule_id)
    db.commit()
    return APIResponse(
        message="Discount rule submitted",
        data=DiscountRuleResponse.model_validate(row),
    )


@discount_rules_router.post("/{rule_id}/approve", response_model=APIResponse[dict])
def approve_discount_rule(
    rule_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.discount_rule:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = DiscountService(db).approve(ctx, rule_id)
    db.commit()
    return APIResponse(message="Discount rule approved", data={"status": instance.status})
