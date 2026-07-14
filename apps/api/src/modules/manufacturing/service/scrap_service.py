"""Scrap application service."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.manufacturing.domain.enums import MfgEntityType, ScrapStatus
from modules.manufacturing.models.scrap import MfgScrap
from modules.manufacturing.repository.production_order_repository import ProductionOrderRepository
from modules.manufacturing.repository.scrap_repository import ScrapRepository
from modules.manufacturing.repository.wip_repository import WipRepository
from modules.manufacturing.service.document_number_service import DocumentNumberService
from modules.manufacturing.service.engines import ProductionEngine, ScrapEngine, WipEngine
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator
from modules.manufacturing.service.posting_service import ManufacturingPostingService


class ScrapService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ScrapRepository(db)
        self._orders = ProductionOrderRepository(db)
        self._wip = WipRepository(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ScrapEngine()
        self._prod = ProductionEngine()
        self._wip_engine = WipEngine()
        self._posting = ManufacturingPostingService(db)
        self._scope = MfgScopeValidator(db)
        self._audit = AuditService(db)

    def list_scraps(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_scraps(ctx, cid)

    def get_scrap(self, ctx: TenantContext, scrap_id: UUID) -> MfgScrap:
        row = self._repo.get(ctx, scrap_id)
        if row is None:
            raise NotFoundException("Scrap not found")
        return row

    def create_scrap(self, ctx: TenantContext, **fields) -> MfgScrap:
        company_id = fields["company_id"]
        self._scope.validate_company_access(ctx, company_id)
        fields["branch_id"] = self._scope.require_branch(ctx, fields.get("branch_id"))
        number = self._numbers.generate(
            MfgEntityType.SCRAP, company_id, model=MfgScrap, code_column="document_number"
        )
        qty = Decimal(str(fields.pop("quantity")))
        unit = Decimal(str(fields.get("unit_cost") or 0))
        scrap = self._repo.create(
            ctx,
            document_number=number,
            document_date=fields.get("document_date") or date.today(),
            quantity=qty,
            unit_cost=float(unit) if fields.get("unit_cost") is not None else None,
            total_cost=float((qty * unit).quantize(Decimal("0.0001"))),
            status=ScrapStatus.DRAFT.value,
            **{k: v for k, v in fields.items() if k not in {"document_date", "unit_cost"}},
        )
        return self.get_scrap(ctx, scrap.id)

    def submit(self, ctx: TenantContext, scrap_id: UUID) -> MfgScrap:
        scrap = self.get_scrap(ctx, scrap_id)
        self._engine.validate_submittable(scrap)
        self._repo.update(ctx, scrap_id, status=ScrapStatus.SUBMITTED.value, workflow_status="submitted")
        return self.get_scrap(ctx, scrap_id)

    def approve(self, ctx: TenantContext, scrap_id: UUID) -> MfgScrap:
        scrap = self.get_scrap(ctx, scrap_id)
        self._engine.validate_approvable(scrap)
        self._repo.update(ctx, scrap_id, status=ScrapStatus.APPROVED.value, workflow_status="approved")
        return self.get_scrap(ctx, scrap_id)

    def post(
        self,
        ctx: TenantContext,
        scrap_id: UUID,
        *,
        scrap_expense_account_id: UUID,
        wip_account_id: UUID,
        fiscal_year_id: UUID | None = None,
    ) -> MfgScrap:
        scrap = self.get_scrap(ctx, scrap_id)
        self._engine.validate_postable(scrap)
        amount = self._engine.compute_total_cost(scrap)
        order = self._orders.get(ctx, scrap.production_order_id)
        if order is not None:
            self._prod.apply_scrap_qty(order, Decimal(str(scrap.quantity)))
        wip = self._wip.get_by_order(ctx, scrap.production_order_id)
        if wip is not None and amount > 0:
            self._wip_engine.relieve_material(wip, amount)
        if amount > 0:
            self._posting.post_scrap(
                ctx,
                scrap,
                amount=amount,
                scrap_expense_account_id=scrap_expense_account_id,
                wip_account_id=wip_account_id,
                fiscal_year_id=fiscal_year_id,
            )
        self._repo.update(ctx, scrap_id, status=ScrapStatus.POSTED.value)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_scrap",
            entity_id=scrap_id,
            operation="post",
            performed_by=ctx.user_id,
        )
        return self.get_scrap(ctx, scrap_id)
