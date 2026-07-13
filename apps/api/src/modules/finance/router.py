"""Finance module router aggregation."""

from fastapi import APIRouter

from modules.finance.routers import (
    account_groups_router,
    ap_router,
    ar_router,
    asset_transactions_router,
    chart_of_accounts_router,
    currency_rates_router,
    fiscal_years_router,
    gl_router,
    journals_router,
    periods_router,
    reports_router,
    tax_register_router,
)

finance_router = APIRouter(prefix="/finance")
finance_router.include_router(account_groups_router)
finance_router.include_router(chart_of_accounts_router)
finance_router.include_router(fiscal_years_router)
finance_router.include_router(periods_router)
finance_router.include_router(journals_router)
finance_router.include_router(gl_router)
finance_router.include_router(ar_router)
finance_router.include_router(ap_router)
finance_router.include_router(tax_register_router)
finance_router.include_router(currency_rates_router)
finance_router.include_router(asset_transactions_router)
finance_router.include_router(reports_router)
