"""Production order application service."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.manufacturing.domain.enums import MfgEntityType, ProductionOrderStatus, VarianceType
from modules.manufacturing.domain.exceptions import InvalidBomState
from modules.manufacturing.models.production_order import MfgProductionOrder
from modules.manufacturing.repository.bom_repository import BomRepository
from modules.manufacturing.repository.production_order_repository import ProductionOrderRepository
from modules.manufacturing.repository.routing_repository import RoutingRepository
from modules.manufacturing.repository.variance_repository import VarianceRepository
from modules.manufacturing.repository.wip_repository import WipRepository
from modules.manufacturing.service.document_number_service import DocumentNumberService
from modules.manufacturing.service.engines import (
    ProductionEngine,
    RoutingEngine,
    VarianceEngine,
    WipEngine,
)
from modules.manufacturing.service.mfg_scope_validator import MfgScopeValidator


class ProductionOrderService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = ProductionOrderRepository(db)
        self._boms = BomRepository(db)
        self._routings = RoutingRepository(db)
        self._wip = WipRepository(db)
        self._variances = VarianceRepository(db)
        self._numbers = DocumentNumberService(db)
        self._engine = ProductionEngine()
        self._routing_engine = RoutingEngine()
        self._wip_engine = WipEngine()
        self._variance_engine = VarianceEngine()
        self._scope = MfgScopeValidator(db)
        self._audit = AuditService(db)

    def list_orders(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_orders(ctx, cid)

    def get_order(self, ctx: TenantContext, order_id: UUID) -> MfgProductionOrder:
        row = self._repo.get(ctx, order_id)
        if row is None:
            raise NotFoundException("Production order not found")
        return row

    def create_order(
        self,
        ctx: TenantContext,
        *,
        company_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        bom_id: UUID,
        warehouse_id: UUID,
        planned_qty: Decimal,
        uom_id: UUID,
        document_date: date | None = None,
        routing_id: UUID | None = None,
        cost_center_id: UUID | None = None,
        source_module: str | None = None,
        source_document_id: UUID | None = None,
        planned_start=None,
        planned_end=None,
    ) -> MfgProductionOrder:
        self._scope.validate_company_access(ctx, company_id)
        branch_id = self._scope.require_branch(ctx, branch_id)
        bom = self._boms.get(ctx, bom_id)
        if bom is None or bom.status != "active":
            raise InvalidBomState("Active BOM required")
        if bom.product_id != product_id:
            raise InvalidBomState("BOM product mismatch")
        number = self._numbers.generate(
            MfgEntityType.PRODUCTION_ORDER,
            company_id,
            model=MfgProductionOrder,
            code_column="document_number",
        )
        order = self._repo.create(
            ctx,
            company_id=company_id,
            branch_id=branch_id,
            document_number=number,
            document_date=document_date or date.today(),
            product_id=product_id,
            bom_id=bom_id,
            routing_id=routing_id,
            warehouse_id=warehouse_id,
            planned_qty=planned_qty,
            completed_qty=0,
            scrapped_qty=0,
            uom_id=uom_id,
            planned_start=planned_start,
            planned_end=planned_end,
            status=ProductionOrderStatus.DRAFT.value,
            cost_center_id=cost_center_id,
            source_module=source_module,
            source_document_id=source_document_id,
        )
        return self.get_order(ctx, order.id)

    def update_order(self, ctx: TenantContext, order_id: UUID, **fields) -> MfgProductionOrder:
        order = self.get_order(ctx, order_id)
        if order.status != ProductionOrderStatus.DRAFT.value:
            fields = {k: v for k, v in fields.items() if k in {"planned_start", "planned_end"}}
        self._repo.update(ctx, order_id, **fields)
        return self.get_order(ctx, order_id)

    def release(self, ctx: TenantContext, order_id: UUID) -> MfgProductionOrder:
        order = self.get_order(ctx, order_id)
        self._engine.validate_releasable(order)
        if order.routing_id:
            routing = self._routings.get(ctx, order.routing_id)
            if routing is not None:
                for tmpl in self._routing_engine.build_operations(
                    routing, Decimal(str(order.planned_qty))
                ):
                    self._repo.add_operation(
                        ctx,
                        order,
                        operation_seq=tmpl.operation_seq,
                        routing_operation_id=tmpl.routing_operation_id,
                        work_center_id=tmpl.work_center_id,
                        planned_qty=float(order.planned_qty),
                        produced_qty=0,
                        rejected_qty=0,
                        status="pending",
                    )
        self._wip.create(
            ctx,
            company_id=order.company_id,
            branch_id=order.branch_id,
            production_order_id=order.id,
            material_cost=0,
            labor_cost=0,
            overhead_cost=0,
            total_cost=0,
            status="open",
        )
        self._repo.update(
            ctx,
            order_id,
            status=ProductionOrderStatus.RELEASED.value,
            workflow_status="released",
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_production_order",
            entity_id=order_id,
            operation="release",
            performed_by=ctx.user_id,
        )
        return self.get_order(ctx, order_id)

    def start(self, ctx: TenantContext, order_id: UUID) -> MfgProductionOrder:
        order = self.get_order(ctx, order_id)
        self._engine.apply_start(order)
        self._db.flush()
        return self.get_order(ctx, order_id)

    def complete(self, ctx: TenantContext, order_id: UUID) -> MfgProductionOrder:
        order = self.get_order(ctx, order_id)
        self._engine.apply_complete(order)
        self._db.flush()
        return self.get_order(ctx, order_id)

    def close(self, ctx: TenantContext, order_id: UUID, *, standard_material_cost: Decimal | None = None) -> MfgProductionOrder:
        order = self.get_order(ctx, order_id)
        self._engine.apply_close(order)
        wip = self._wip.get_by_order(ctx, order_id)
        if wip is not None:
            actual = Decimal(str(wip.total_cost or 0))
            standard = standard_material_cost if standard_material_cost is not None else actual
            result = self._variance_engine.compute(
                variance_type=VarianceType.MATERIAL.value,
                standard_amount=standard,
                actual_amount=actual,
            )
            if result.variance_amount != 0:
                self._variances.create(
                    ctx,
                    company_id=order.company_id,
                    branch_id=order.branch_id,
                    production_order_id=order.id,
                    variance_type=result.variance_type,
                    standard_amount=float(result.standard_amount),
                    actual_amount=float(result.actual_amount),
                    variance_amount=float(result.variance_amount),
                    status="open",
                    period_id=order.period_id,
                )
            self._wip_engine.close(wip)
            self._db.flush()
        self._db.flush()
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mfg_production_order",
            entity_id=order_id,
            operation="close",
            performed_by=ctx.user_id,
        )
        return self.get_order(ctx, order_id)

    def cancel(self, ctx: TenantContext, order_id: UUID) -> MfgProductionOrder:
        order = self.get_order(ctx, order_id)
        self._engine.apply_cancel(order)
        self._db.flush()
        return self.get_order(ctx, order_id)

    def update_operation(
        self,
        ctx: TenantContext,
        order_id: UUID,
        operation_id: UUID,
        **fields,
    ) -> MfgProductionOrder:
        order = self.get_order(ctx, order_id)
        op = next((o for o in order.operations if o.id == operation_id and not o.is_deleted), None)
        if op is None:
            raise NotFoundException("Operation not found")
        for k, v in fields.items():
            if v is not None:
                setattr(op, k, v)
        self._db.flush()
        return self.get_order(ctx, order_id)
