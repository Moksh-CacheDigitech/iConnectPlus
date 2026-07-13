"""Fiscal year and period routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.finance.schemas import (
    FiscalYearCreateRequest,
    FiscalYearResponse,
    PeriodCloseFlagsRequest,
    PeriodResponse,
)
from modules.finance.service.fiscal_year_service import FiscalYearService
from modules.finance.service.period_service import PeriodService
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from shared.schemas import APIResponse

fiscal_years_router = APIRouter(prefix="/fiscal-years", tags=["Finance - Fiscal Years"])
periods_router = APIRouter(prefix="/periods", tags=["Finance - Periods"])


@fiscal_years_router.get("", response_model=APIResponse[list[FiscalYearResponse]])
def list_fiscal_years(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.fiscal_year:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[list[FiscalYearResponse]]:
    years = FiscalYearService(db).list_fiscal_years(ctx, company_id)
    return APIResponse(message="Fiscal years retrieved", data=[FiscalYearResponse.model_validate(y) for y in years])


@fiscal_years_router.post("", response_model=APIResponse[FiscalYearResponse])
def create_fiscal_year(
    body: FiscalYearCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.fiscal_year:create"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
) -> APIResponse[FiscalYearResponse]:
    fy = FiscalYearService(db).create_fiscal_year(ctx, company_id=company_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Fiscal year created", data=FiscalYearResponse.model_validate(fy))


@fiscal_years_router.post("/{fiscal_year_id}/close", response_model=APIResponse[FiscalYearResponse])
def close_fiscal_year(
    fiscal_year_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.fiscal_year:close"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[FiscalYearResponse]:
    fy = FiscalYearService(db).close_fiscal_year(ctx, fiscal_year_id)
    db.commit()
    return APIResponse(message="Fiscal year closed", data=FiscalYearResponse.model_validate(fy))


@periods_router.get("", response_model=APIResponse[list[PeriodResponse]])
def list_periods(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.period:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
    fiscal_year_id: UUID | None = None,
) -> APIResponse[list[PeriodResponse]]:
    periods = PeriodService(db).list_periods(ctx, company_id, fiscal_year_id)
    return APIResponse(message="Periods retrieved", data=[PeriodResponse.model_validate(p) for p in periods])


@periods_router.post("/{period_id}/soft-close", response_model=APIResponse[PeriodResponse])
def soft_close_period(
    period_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.period:close"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PeriodResponse]:
    period = PeriodService(db).soft_close(ctx, period_id)
    db.commit()
    return APIResponse(message="Period soft closed", data=PeriodResponse.model_validate(period))


@periods_router.post("/{period_id}/hard-close", response_model=APIResponse[PeriodResponse])
def hard_close_period(
    period_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.period:close"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PeriodResponse]:
    period = PeriodService(db).hard_close(ctx, period_id)
    db.commit()
    return APIResponse(message="Period hard closed", data=PeriodResponse.model_validate(period))


@periods_router.post("/{period_id}/reopen", response_model=APIResponse[PeriodResponse])
def reopen_period(
    period_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.period:reopen"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PeriodResponse]:
    period = PeriodService(db).reopen(ctx, period_id)
    db.commit()
    return APIResponse(message="Period reopened", data=PeriodResponse.model_validate(period))


@periods_router.patch("/{period_id}/flags", response_model=APIResponse[PeriodResponse])
def update_period_flags(
    period_id: UUID,
    body: PeriodCloseFlagsRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.period:close"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[PeriodResponse]:
    period = PeriodService(db).update_close_flags(ctx, period_id, **body.model_dump(exclude_unset=True))
    db.commit()
    return APIResponse(message="Period flags updated", data=PeriodResponse.model_validate(period))
