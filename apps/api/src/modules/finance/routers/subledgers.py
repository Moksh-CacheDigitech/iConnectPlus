"""AR/AP sub-ledger routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.finance.dependencies import PaginationParams, get_pagination, paginate
from modules.finance.schemas import (
    CustomerLedgerCreateRequest,
    CustomerLedgerResponse,
    PaymentRequest,
    VendorLedgerCreateRequest,
    VendorLedgerResponse,
)
from modules.finance.service.customer_ledger_service import CustomerLedgerService
from modules.finance.service.vendor_ledger_service import VendorLedgerService
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from shared.schemas import APIResponse

ar_router = APIRouter(prefix="/ar", tags=["Finance - Accounts Receivable"])
ap_router = APIRouter(prefix="/ap", tags=["Finance - Accounts Payable"])


@ar_router.get("", response_model=APIResponse[list[CustomerLedgerResponse]])
def list_ar(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.ar:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    customer_id: UUID | None = None,
) -> APIResponse[list[CustomerLedgerResponse]]:
    entries = CustomerLedgerService(db).list_entries(ctx, company_id, customer_id)
    page = paginate(entries, pagination)
    return APIResponse(
        message="AR entries retrieved",
        data=[CustomerLedgerResponse.model_validate(e) for e in page],
    )


@ar_router.post("", response_model=APIResponse[CustomerLedgerResponse])
def create_ar(
    body: CustomerLedgerCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.ar:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CustomerLedgerResponse]:
    entry = CustomerLedgerService(db).create_entry(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="AR entry created", data=CustomerLedgerResponse.model_validate(entry))


@ar_router.post("/{entry_id}/payment", response_model=APIResponse[CustomerLedgerResponse])
def ar_payment(
    entry_id: UUID,
    body: PaymentRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.ar:payment"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CustomerLedgerResponse]:
    entry = CustomerLedgerService(db).record_payment(ctx, entry_id, body.amount)
    db.commit()
    return APIResponse(message="AR payment recorded", data=CustomerLedgerResponse.model_validate(entry))


@ap_router.get("", response_model=APIResponse[list[VendorLedgerResponse]])
def list_ap(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.ap:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    vendor_id: UUID | None = None,
) -> APIResponse[list[VendorLedgerResponse]]:
    entries = VendorLedgerService(db).list_entries(ctx, company_id, vendor_id)
    page = paginate(entries, pagination)
    return APIResponse(
        message="AP entries retrieved",
        data=[VendorLedgerResponse.model_validate(e) for e in page],
    )


@ap_router.post("", response_model=APIResponse[VendorLedgerResponse])
def create_ap(
    body: VendorLedgerCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.ap:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[VendorLedgerResponse]:
    entry = VendorLedgerService(db).create_entry(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="AP entry created", data=VendorLedgerResponse.model_validate(entry))


@ap_router.post("/{entry_id}/payment", response_model=APIResponse[VendorLedgerResponse])
def ap_payment(
    entry_id: UUID,
    body: PaymentRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.ap:payment"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[VendorLedgerResponse]:
    entry = VendorLedgerService(db).record_payment(ctx, entry_id, body.amount)
    db.commit()
    return APIResponse(message="AP payment recorded", data=VendorLedgerResponse.model_validate(entry))
