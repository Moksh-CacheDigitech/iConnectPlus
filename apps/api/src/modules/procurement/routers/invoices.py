"""Procurement purchase invoice routers."""

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
    InvoiceCreateRequest,
    InvoicePostRequest,
    InvoiceResponse,
    InvoiceUpdateRequest,
    WorkflowActionRequest,
)
from modules.procurement.service.invoice_service import InvoiceService
from modules.procurement.service.procurement_posting_service import ProcurementPostingService
from shared.schemas import APIResponse

invoices_router = APIRouter(prefix="/invoices", tags=["Procurement - Invoices"])


@invoices_router.get("", response_model=APIResponse[list[InvoiceResponse]])
def list_invoices(
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.invoice:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[InvoiceResponse]]:
    rows = InvoiceService(db).list_invoices(ctx, company_id)
    page = paginate(rows, pagination)
    return APIResponse(
        message="Invoices retrieved",
        data=[InvoiceResponse.model_validate(r) for r in page],
    )


@invoices_router.post("", response_model=APIResponse[InvoiceResponse])
def create_invoice(
    body: InvoiceCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.invoice:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).create_from_grn(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Invoice created", data=InvoiceResponse.model_validate(row))


@invoices_router.get("/{invoice_id}", response_model=APIResponse[InvoiceResponse])
def get_invoice(
    invoice_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.invoice:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).get_invoice(ctx, invoice_id)
    return APIResponse(message="Invoice retrieved", data=InvoiceResponse.model_validate(row))


@invoices_router.patch("/{invoice_id}", response_model=APIResponse[InvoiceResponse])
def update_invoice(
    invoice_id: UUID,
    body: InvoiceUpdateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.invoice:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).update(ctx, invoice_id, **extract_update_fields(body))
    db.commit()
    return APIResponse(message="Invoice updated", data=InvoiceResponse.model_validate(row))


@invoices_router.post("/{invoice_id}/submit", response_model=APIResponse[InvoiceResponse])
def submit_invoice(
    invoice_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.invoice:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).submit(ctx, invoice_id)
    db.commit()
    return APIResponse(message="Invoice submitted", data=InvoiceResponse.model_validate(row))


@invoices_router.post("/{invoice_id}/approve", response_model=APIResponse[dict])
def approve_invoice(
    invoice_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.invoice:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = InvoiceService(db).approve(ctx, invoice_id)
    db.commit()
    return APIResponse(message="Invoice approved", data={"status": instance.status})


@invoices_router.post("/{invoice_id}/post", response_model=APIResponse[InvoiceResponse])
def post_invoice(
    invoice_id: UUID,
    body: InvoicePostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.invoice:post"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = ProcurementPostingService(db).post_invoice(
        ctx,
        invoice_id,
        ap_account_id=body.ap_account_id,
        expense_account_id=body.expense_account_id,
    )
    db.commit()
    return APIResponse(message="Invoice posted", data=InvoiceResponse.model_validate(row))


@invoices_router.post("/{invoice_id}/cancel", response_model=APIResponse[InvoiceResponse])
def cancel_invoice(
    invoice_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.invoice:cancel"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).cancel(ctx, invoice_id)
    db.commit()
    return APIResponse(message="Invoice cancelled", data=InvoiceResponse.model_validate(row))
