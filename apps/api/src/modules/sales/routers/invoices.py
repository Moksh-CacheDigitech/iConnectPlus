"""Invoice routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.sales.dependencies import PaginationParams, get_pagination, paginate
from modules.sales.schemas import (
    InvoiceCreateRequest,
    InvoicePostRequest,
    InvoiceResponse,
    WorkflowActionRequest,
)
from modules.sales.service.invoice_service import InvoiceService
from modules.sales.service.sales_posting_service import SalesPostingService
from shared.schemas import APIResponse

invoices_router = APIRouter(prefix="/invoices", tags=["Sales - Invoices"])


@invoices_router.get("", response_model=APIResponse[list[InvoiceResponse]])
def list_invoices(
    ctx: Annotated[TenantContext, Depends(require_permission("sales.invoice:read"))],
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
    ctx: Annotated[TenantContext, Depends(require_permission("sales.invoice:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).create_from_delivery(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Invoice created", data=InvoiceResponse.model_validate(row))


@invoices_router.get("/{invoice_id}", response_model=APIResponse[InvoiceResponse])
def get_invoice(
    invoice_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.invoice:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).get_invoice(ctx, invoice_id)
    return APIResponse(message="Invoice retrieved", data=InvoiceResponse.model_validate(row))


@invoices_router.post("/{invoice_id}/submit", response_model=APIResponse[InvoiceResponse])
def submit_invoice(
    invoice_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.invoice:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).submit(ctx, invoice_id)
    db.commit()
    return APIResponse(message="Invoice submitted", data=InvoiceResponse.model_validate(row))


@invoices_router.post("/{invoice_id}/approve", response_model=APIResponse[dict])
def approve_invoice(
    invoice_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.invoice:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = InvoiceService(db).approve(ctx, invoice_id)
    db.commit()
    return APIResponse(message="Invoice approved", data={"status": instance.status})


@invoices_router.post("/{invoice_id}/post", response_model=APIResponse[InvoiceResponse])
def post_invoice(
    invoice_id: UUID,
    body: InvoicePostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.invoice:post"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = SalesPostingService(db).post_invoice(
        ctx,
        invoice_id,
        ar_account_id=body.ar_account_id,
        revenue_account_id=body.revenue_account_id,
    )
    db.commit()
    return APIResponse(message="Invoice posted", data=InvoiceResponse.model_validate(row))


@invoices_router.post("/{invoice_id}/cancel", response_model=APIResponse[InvoiceResponse])
def cancel_invoice(
    invoice_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("sales.invoice:cancel"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[InvoiceResponse]:
    row = InvoiceService(db).cancel(ctx, invoice_id)
    db.commit()
    return APIResponse(message="Invoice cancelled", data=InvoiceResponse.model_validate(row))
