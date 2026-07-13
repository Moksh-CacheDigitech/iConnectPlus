"""Tax, currency, asset, and report routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.finance.schemas import (
    AssetTransactionCreateRequest,
    AssetTransactionResponse,
    CurrencyRateCreateRequest,
    CurrencyRateResponse,
    TaxRegisterResponse,
    TrialBalanceLineResponse,
)
from modules.finance.service.asset_accounting_service import AssetAccountingService
from modules.finance.service.currency_service import CurrencyService
from modules.finance.service.report_service import ReportService
from modules.finance.service.tax_service import TaxService
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from shared.schemas import APIResponse

tax_register_router = APIRouter(prefix="/tax-register", tags=["Finance - Tax Register"])
currency_rates_router = APIRouter(prefix="/currency-rates", tags=["Finance - Currency Rates"])
asset_transactions_router = APIRouter(prefix="/asset-transactions", tags=["Finance - Asset Transactions"])
reports_router = APIRouter(prefix="/reports", tags=["Finance - Reports"])


@tax_register_router.get("", response_model=APIResponse[list[TaxRegisterResponse]])
def list_tax_register(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.tax:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
    period_id: UUID | None = None,
) -> APIResponse[list[TaxRegisterResponse]]:
    rows = TaxService(db).list_register(ctx, company_id, period_id)
    return APIResponse(
        message="Tax register retrieved",
        data=[TaxRegisterResponse.model_validate(r) for r in rows],
    )


@currency_rates_router.get("", response_model=APIResponse[list[CurrencyRateResponse]])
def list_currency_rates(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.currency_rate:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[list[CurrencyRateResponse]]:
    rates = CurrencyService(db).list_rates(ctx, company_id)
    return APIResponse(
        message="Currency rates retrieved",
        data=[CurrencyRateResponse.model_validate(r) for r in rates],
    )


@currency_rates_router.post("", response_model=APIResponse[CurrencyRateResponse])
def create_currency_rate(
    body: CurrencyRateCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.currency_rate:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[CurrencyRateResponse]:
    rate = CurrencyService(db).create_rate(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Currency rate created", data=CurrencyRateResponse.model_validate(rate))


@asset_transactions_router.get("", response_model=APIResponse[list[AssetTransactionResponse]])
def list_asset_transactions(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.asset_transaction:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[list[AssetTransactionResponse]]:
    txns = AssetAccountingService(db).list_transactions(ctx, company_id)
    return APIResponse(
        message="Asset transactions retrieved",
        data=[AssetTransactionResponse.model_validate(t) for t in txns],
    )


@asset_transactions_router.post("", response_model=APIResponse[AssetTransactionResponse])
def create_asset_transaction(
    body: AssetTransactionCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.asset_transaction:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[AssetTransactionResponse]:
    txn = AssetAccountingService(db).create_transaction(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Asset transaction created", data=AssetTransactionResponse.model_validate(txn))


@reports_router.get("/trial-balance", response_model=APIResponse[list[TrialBalanceLineResponse]])
def trial_balance(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    period_id: UUID,
    company_id: UUID | None = None,
) -> APIResponse[list[TrialBalanceLineResponse]]:
    lines = ReportService(db).trial_balance(ctx, period_id, company_id)
    return APIResponse(
        message="Trial balance generated",
        data=[
            TrialBalanceLineResponse(
                account_id=line.account_id,
                account_code=line.account_code,
                account_name=line.account_name,
                debit_total=float(line.debit_total),
                credit_total=float(line.credit_total),
                balance=float(line.balance),
            )
            for line in lines
        ],
    )


@reports_router.get("/ar-aging", response_model=APIResponse[list[dict]])
def ar_aging(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[list[dict]]:
    entries = ReportService(db).ar_aging(ctx, company_id)
    return APIResponse(
        message="AR aging report generated",
        data=[
            {
                "id": str(e.id),
                "customer_id": str(e.customer_id),
                "document_number": e.document_number,
                "due_date": str(e.due_date),
                "balance_amount": float(e.balance_amount),
                "aging_bucket": e.aging_bucket,
            }
            for e in entries
        ],
    )


@reports_router.get("/ap-aging", response_model=APIResponse[list[dict]])
def ap_aging(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[list[dict]]:
    entries = ReportService(db).ap_aging(ctx, company_id)
    return APIResponse(
        message="AP aging report generated",
        data=[
            {
                "id": str(e.id),
                "vendor_id": str(e.vendor_id),
                "document_number": e.document_number,
                "due_date": str(e.due_date),
                "balance_amount": float(e.balance_amount),
                "aging_bucket": e.aging_bucket,
            }
            for e in entries
        ],
    )
