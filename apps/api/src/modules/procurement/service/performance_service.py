"""Vendor performance read-only service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.repository.performance_repository import PerformanceRepository
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator


class PerformanceService:
    def __init__(self, db: Session) -> None:
        self._repo = PerformanceRepository(db)
        self._scope = ProcurementScopeValidator(db)

    def list_performance(
        self,
        ctx: TenantContext,
        company_id: UUID | None = None,
        *,
        vendor_id: UUID | None = None,
    ):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_performance(ctx, cid, vendor_id=vendor_id)
