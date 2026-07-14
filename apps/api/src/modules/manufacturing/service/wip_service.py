"""WIP and variance services."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.domain.enums import VarianceStatus
from modules.manufacturing.models.variance import MfgVariance
from modules.manufacturing.models.wip import MfgWip
from modules.manufacturing.repository.production_order_repository import ProductionOrderRepository
from modules.manufacturing.repository.variance_repository import VarianceRepository
from modules.manufacturing.repository.wip_repository import WipRepository
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator
from modules.manufacturing.service.posting_service import ManufacturingPostingService


class WipService:
    def __init__(self, db: Session) -> None:
        self._repo = WipRepository(db)
        self._scope = MfgScopeValidator(db)

    def list_wip(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_wip(ctx, cid)

    def get_wip(self, ctx: TenantContext, wip_id: UUID) -> MfgWip:
        row = self._repo.get(ctx, wip_id)
        if row is None:
            raise NotFoundException("WIP not found")
        return row

    def get_by_order(self, ctx: TenantContext, production_order_id: UUID) -> MfgWip:
        row = self._repo.get_by_order(ctx, production_order_id)
        if row is None:
            raise NotFoundException("WIP not found for order")
        return row


class VarianceService:
    def __init__(self, db: Session) -> None:
        self._repo = VarianceRepository(db)
        self._orders = ProductionOrderRepository(db)
        self._posting = ManufacturingPostingService(db)
        self._scope = MfgScopeValidator(db)

    def list_variances(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_variances(ctx, cid)

    def get_variance(self, ctx: TenantContext, variance_id: UUID) -> MfgVariance:
        row = self._repo.get(ctx, variance_id)
        if row is None:
            raise NotFoundException("Variance not found")
        return row

    def post(
        self,
        ctx: TenantContext,
        variance_id: UUID,
        *,
        variance_account_id: UUID,
        wip_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> MfgVariance:
        variance = self.get_variance(ctx, variance_id)
        if variance.status != VarianceStatus.OPEN.value:
            raise NotFoundException("Variance already posted")
        order = self._orders.get(ctx, variance.production_order_id)
        amount = Decimal(str(variance.variance_amount))
        if amount != 0 and variance.period_id is not None:
            self._posting.post_variance(
                ctx,
                variance,
                amount=amount,
                variance_account_id=variance_account_id,
                wip_account_id=wip_account_id,
                fiscal_year_id=fiscal_year_id,
                journal_date=order.document_date if order else None,
            )
        self._repo.update(ctx, variance_id, status=VarianceStatus.POSTED.value)
        return self.get_variance(ctx, variance_id)
