"""Manufacturing report service."""

from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.manufacturing.repository.bom_repository import BomRepository
from modules.manufacturing.repository.machine_repository import MachineRepository
from modules.manufacturing.repository.production_order_repository import ProductionOrderRepository
from modules.manufacturing.repository.scrap_repository import ScrapRepository
from modules.manufacturing.repository.wip_repository import WipRepository
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator


class ManufacturingReportService:
    def __init__(self, db: Session) -> None:
        self._boms = BomRepository(db)
        self._orders = ProductionOrderRepository(db)
        self._wip = WipRepository(db)
        self._scraps = ScrapRepository(db)
        self._machines = MachineRepository(db)
        self._scope = MfgScopeValidator(db)

    def bom_summary(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        rows = self._boms.list_boms(ctx, cid)
        data = [
            {
                "bom_id": str(r.id),
                "bom_number": r.bom_number,
                "product_id": str(r.product_id),
                "status": r.status,
                "line_count": len([ln for ln in r.lines if not ln.is_deleted]),
            }
            for r in rows
        ]
        return {"name": "bom-summary", "row_count": len(data), "rows": data}

    def wo_summary(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        rows = self._orders.list_orders(ctx, cid)
        data = [
            {
                "order_id": str(r.id),
                "document_number": r.document_number,
                "product_id": str(r.product_id),
                "status": r.status,
                "planned_qty": float(r.planned_qty),
                "completed_qty": float(r.completed_qty),
            }
            for r in rows
        ]
        return {"name": "wo-summary", "row_count": len(data), "rows": data}

    def wip_summary(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        rows = self._wip.list_wip(ctx, cid)
        data = [
            {
                "wip_id": str(r.id),
                "production_order_id": str(r.production_order_id),
                "total_cost": float(r.total_cost),
                "status": r.status,
            }
            for r in rows
        ]
        return {"name": "wip-summary", "row_count": len(data), "rows": data}

    def scrap_summary(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        rows = self._scraps.list_scraps(ctx, cid)
        data = [
            {
                "scrap_id": str(r.id),
                "document_number": r.document_number,
                "quantity": float(r.quantity),
                "status": r.status,
            }
            for r in rows
        ]
        return {"name": "scrap-summary", "row_count": len(data), "rows": data}

    def machine_utilization(self, ctx: TenantContext, company_id: UUID | None = None) -> dict:
        cid = self._scope.resolve_company_id(ctx, company_id)
        rows = self._machines.list_machines(ctx, cid)
        data = [
            {
                "machine_id": str(r.id),
                "machine_code": r.machine_code,
                "status": r.status,
            }
            for r in rows
        ]
        return {"name": "machine-utilization", "row_count": len(data), "rows": data}
