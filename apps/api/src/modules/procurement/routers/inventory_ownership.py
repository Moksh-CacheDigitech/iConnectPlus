"""Inventory accountability: owner-tagged stock, aging, open-for-sale, transfer requests,
and shipment milestones on vendor POs."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_any_permission, require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.rbac_service import RBACService
from modules.procurement.schemas import (
    InventoryAgingReport,
    InventoryAssignOwnerRequest,
    InventoryOpenForSaleRequest,
    InventoryTransferCreate,
    InventoryTransferDecision,
    InventoryTransferResponse,
    InventoryUnitRow,
    ScmDeliveryMilestoneRequest,
    ScmDeliveryMilestoneResponse,
)
from modules.procurement.service.inventory_ownership_service import InventoryOwnershipService
from modules.procurement.service.scm_delivery_notification_service import ScmDeliveryNotificationService
from shared.schemas import APIResponse

inventory_ownership_router = APIRouter(prefix="/scm", tags=["Procurement - Inventory ownership"])

# Stock is visible to the whole office - SCM and every salesperson.
_INVENTORY_READ = require_any_permission("procurement.order:read", "crm.opportunity:read")


def _is_scm_admin(db: Session, ctx: TenantContext) -> bool:
    if ctx.user_type in {"super_admin", "tenant_admin"}:
        return True
    return RBACService(db).has_permission(ctx.user_id, ctx.tenant_id, "procurement.order:create")


@inventory_ownership_router.get("/inventory/units", response_model=APIResponse[list[InventoryUnitRow]])
def list_inventory_units(
    ctx: Annotated[TenantContext, Depends(_INVENTORY_READ)],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=InventoryOwnershipService(db).list_units(ctx, company_id))


@inventory_ownership_router.get("/inventory/aging", response_model=APIResponse[InventoryAgingReport])
def inventory_aging_report(
    ctx: Annotated[TenantContext, Depends(_INVENTORY_READ)],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    return APIResponse(message="OK", data=InventoryOwnershipService(db).aging_report(ctx, company_id))


@inventory_ownership_router.get("/inventory/suggest", response_model=APIResponse[list[InventoryUnitRow]])
def suggest_inventory(
    ctx: Annotated[TenantContext, Depends(_INVENTORY_READ)],
    db: Annotated[Session, Depends(get_db)],
    q: Annotated[str, Query(min_length=2, max_length=120)],
    company_id: UUID | None = None,
):
    """Matching stock already on hand, at today's value, before a fresh order is placed."""
    return APIResponse(message="OK", data=InventoryOwnershipService(db).suggest_stock(ctx, q, company_id))


@inventory_ownership_router.post("/inventory/assign-owner", response_model=APIResponse[dict[str, int]])
def assign_inventory_owner(
    body: InventoryAssignOwnerRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.order:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    count = InventoryOwnershipService(db).assign_owner(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Owner updated", data={"updated": count})


@inventory_ownership_router.post("/inventory/open-for-sale", response_model=APIResponse[dict[str, int]])
def set_inventory_open_for_sale(
    body: InventoryOpenForSaleRequest,
    ctx: Annotated[TenantContext, Depends(_INVENTORY_READ)],
    db: Annotated[Session, Depends(get_db)],
):
    count = InventoryOwnershipService(db).set_open_for_sale(
        ctx, **body.model_dump(), is_scm_admin=_is_scm_admin(db, ctx)
    )
    db.commit()
    return APIResponse(message="Stock availability updated", data={"updated": count})


@inventory_ownership_router.get(
    "/inventory/transfer-requests", response_model=APIResponse[list[InventoryTransferResponse]]
)
def list_inventory_transfers(
    ctx: Annotated[TenantContext, Depends(_INVENTORY_READ)],
    db: Annotated[Session, Depends(get_db)],
    mine: bool = True,
):
    mine_only = mine or not _is_scm_admin(db, ctx)
    return APIResponse(message="OK", data=InventoryOwnershipService(db).list_transfers(ctx, mine_only=mine_only))


@inventory_ownership_router.post(
    "/inventory/transfer-requests", response_model=APIResponse[InventoryTransferResponse]
)
def request_inventory_transfer(
    body: InventoryTransferCreate,
    ctx: Annotated[TenantContext, Depends(_INVENTORY_READ)],
    db: Annotated[Session, Depends(get_db)],
):
    row = InventoryOwnershipService(db).request_transfer(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Request sent to the stock owner", data=row)


@inventory_ownership_router.post(
    "/inventory/transfer-requests/{request_id}/decide",
    response_model=APIResponse[InventoryTransferResponse],
)
def decide_inventory_transfer(
    request_id: UUID,
    body: InventoryTransferDecision,
    ctx: Annotated[TenantContext, Depends(_INVENTORY_READ)],
    db: Annotated[Session, Depends(get_db)],
):
    row = InventoryOwnershipService(db).decide_transfer(
        ctx, request_id, accept=body.accept, remark=body.remark, is_scm_admin=_is_scm_admin(db, ctx)
    )
    db.commit()
    return APIResponse(message="Request accepted" if body.accept else "Request rejected", data=row)


@inventory_ownership_router.patch(
    "/orders/{order_id}/delivery-milestone",
    response_model=APIResponse[ScmDeliveryMilestoneResponse],
)
def update_delivery_milestone(
    order_id: UUID,
    body: ScmDeliveryMilestoneRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.order:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ScmDeliveryNotificationService(db).set_delivery_milestone(ctx, order_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Delivery milestone updated", data=ScmDeliveryMilestoneResponse.model_validate(row))
