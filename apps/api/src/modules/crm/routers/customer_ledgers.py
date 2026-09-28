"""Customer GST registrations, customer PO auto-fetch, and the customer expense (FOC) ledger."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from modules.crm.dependencies import extract_update_fields, get_db
from modules.crm.schemas import (
    CompanyGstCreate,
    CompanyGstResponse,
    CompanyGstUpdate,
    CustomerExpenseAdjustRequest,
    CustomerExpenseCreate,
    CustomerExpenseResponse,
    CustomerExpenseSummaryResponse,
    CustomerExpenseWriteOffRequest,
    CustomerPoExtractRequest,
    CustomerPoExtractResponse,
)
from modules.crm.service.company_gst_service import CompanyGstService, CustomerPoExtractService
from modules.crm.service.customer_expense_service import CustomerExpenseService
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from shared.schemas import APIResponse

customer_ledgers_router = APIRouter(tags=["CRM - Customer GST & Expenses"])


@customer_ledgers_router.get(
    "/companies/{company_account_id}/gst-registrations",
    response_model=APIResponse[list[CompanyGstResponse]],
)
def list_company_gst(
    company_account_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.company:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=CompanyGstService(db).list(ctx, company_account_id))


@customer_ledgers_router.post(
    "/companies/{company_account_id}/gst-registrations",
    response_model=APIResponse[CompanyGstResponse],
)
def create_company_gst(
    company_account_id: UUID,
    body: CompanyGstCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.company:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = CompanyGstService(db).create(ctx, company_account_id, **body.model_dump())
    return APIResponse(message="GST registration added", data=row)


@customer_ledgers_router.patch("/company-gst/{gst_id}", response_model=APIResponse[CompanyGstResponse])
def update_company_gst(
    gst_id: UUID,
    body: CompanyGstUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.company:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = CompanyGstService(db).update(ctx, gst_id, **extract_update_fields(body))
    return APIResponse(message="GST registration updated", data=row)


@customer_ledgers_router.delete("/company-gst/{gst_id}", response_model=APIResponse[dict[str, str]])
def delete_company_gst(
    gst_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.company:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    CompanyGstService(db).delete(ctx, gst_id)
    return APIResponse(message="GST registration removed", data={"id": str(gst_id)})


@customer_ledgers_router.post(
    "/opportunities/{opportunity_id}/customer-po/extract",
    response_model=APIResponse[CustomerPoExtractResponse],
)
def extract_customer_po(
    opportunity_id: UUID,
    body: CustomerPoExtractRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.opportunity:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    """Auto-fetch PO number/date, GSTINs, bill-to/ship-to and lead time from the PO file."""
    data = CustomerPoExtractService(db).extract(ctx, opportunity_id=opportunity_id, **body.model_dump())
    return APIResponse(message="PO details read - review before saving", data=data)


@customer_ledgers_router.get(
    "/companies/{company_account_id}/customer-expenses",
    response_model=APIResponse[list[CustomerExpenseResponse]],
)
def list_customer_expenses(
    company_account_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.company:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=CustomerExpenseService(db).list(ctx, company_account_id))


@customer_ledgers_router.post(
    "/companies/{company_account_id}/customer-expenses",
    response_model=APIResponse[CustomerExpenseResponse],
)
def create_customer_expense(
    company_account_id: UUID,
    body: CustomerExpenseCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.company:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = CustomerExpenseService(db).create(ctx, company_account_id, **body.model_dump())
    return APIResponse(message="Customer expense recorded", data=row)


@customer_ledgers_router.get(
    "/opportunities/{opportunity_id}/customer-expenses/summary",
    response_model=APIResponse[CustomerExpenseSummaryResponse],
)
def opportunity_customer_expense_summary(
    opportunity_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.opportunity:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=CustomerExpenseService(db).summary_for_opportunity(ctx, opportunity_id))


@customer_ledgers_router.post(
    "/customer-expenses/{expense_id}/adjust",
    response_model=APIResponse[CustomerExpenseResponse],
)
def adjust_customer_expense(
    expense_id: UUID,
    body: CustomerExpenseAdjustRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.ovf:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = CustomerExpenseService(db).mark_adjusted(ctx, expense_id, ovf_id=body.ovf_id, remark=body.remark)
    return APIResponse(message="Expense adjusted against OVF", data=row)


@customer_ledgers_router.post(
    "/customer-expenses/{expense_id}/write-off",
    response_model=APIResponse[CustomerExpenseResponse],
)
def write_off_customer_expense(
    expense_id: UUID,
    body: CustomerExpenseWriteOffRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("crm.company:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = CustomerExpenseService(db).write_off(ctx, expense_id, remark=body.remark)
    return APIResponse(message="Expense written off", data=row)
