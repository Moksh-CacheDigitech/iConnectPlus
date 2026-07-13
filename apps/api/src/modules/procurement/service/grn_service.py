"""Goods receipt note (GRN) service."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.procurement.domain.enums import GrnStatus, ProcEntityType
from modules.procurement.models.grn import ProcGrnHeader
from modules.procurement.repository.grn_repository import GrnRepository
from modules.procurement.repository.order_repository import OrderRepository
from modules.procurement.service.document_number_service import DocumentNumberService
from modules.procurement.service.engines.grn_engine import GrnEngine
from modules.procurement.service.inventory.stub_adapter import NoOpInventoryAdapter
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator


class GrnService:
    def __init__(
        self, db: Session, *, inventory_adapter: NoOpInventoryAdapter | None = None
    ) -> None:
        self._db = db
        self._repo = GrnRepository(db)
        self._orders = OrderRepository(db)
        self._scope = ProcurementScopeValidator(db)
        self._engine = GrnEngine()
        self._numbers = DocumentNumberService(db)
        self._inventory = inventory_adapter or NoOpInventoryAdapter()
        self._audit = AuditService(db)

    def list_grns(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_grns(ctx, cid)

    def get_grn(self, ctx: TenantContext, grn_id: UUID) -> ProcGrnHeader:
        row = self._repo.get_grn(ctx, grn_id)
        if row is None:
            raise NotFoundException("GRN not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create_from_order(
        self,
        ctx: TenantContext,
        *,
        order_header_id: UUID,
        document_date,
        warehouse_reference: UUID,
        company_id: UUID | None = None,
        lines: list[dict] | None = None,
    ):
        order = self._orders.get_order(ctx, order_header_id)
        if order is None:
            raise NotFoundException("Purchase order not found")
        self._scope.validate_company_access(ctx, order.company_id)
        self._scope.validate_branch_access(ctx, order.branch_id)
        self._engine.validate_order_for_grn(order)
        cid = self._scope.resolve_company_id(ctx, company_id or order.company_id)
        doc_number = self._numbers.generate(
            ProcEntityType.GRN,
            cid,
            model=ProcGrnHeader,
            code_column="document_number",
        )
        grn = self._repo.create_grn(
            ctx,
            company_id=cid,
            branch_id=order.branch_id,
            document_number=doc_number,
            document_date=document_date,
            order_header_id=order.id,
            vendor_id=order.vendor_id,
            warehouse_reference=warehouse_reference,
            status=GrnStatus.DRAFT.value,
        )
        if lines:
            for spec in lines:
                order_line = next(
                    (ln for ln in order.lines if ln.id == spec["order_line_id"]), None
                )
                if order_line is None:
                    raise NotFoundException("Order line not found")
                qty = Decimal(str(spec["quantity"]))
                self._engine.validate_receive_qty(order_line, qty)
                self._repo.add_line(
                    ctx,
                    grn,
                    order_line_id=order_line.id,
                    line_number=spec["line_number"],
                    product_id=order_line.product_id,
                    quantity=float(qty),
                    uom_id=order_line.uom_id,
                    quantity_rejected=float(spec.get("quantity_rejected", 0)),
                    status="pending",
                )
        else:
            remaining = self._engine.remaining_qty_map(order)
            line_number = 1
            for order_line in [ln for ln in order.lines if not ln.is_deleted]:
                qty = remaining.get(order_line.id, Decimal("0"))
                if qty <= 0:
                    continue
                self._repo.add_line(
                    ctx,
                    grn,
                    order_line_id=order_line.id,
                    line_number=line_number,
                    product_id=order_line.product_id,
                    quantity=float(qty),
                    uom_id=order_line.uom_id,
                    status="pending",
                )
                line_number += 1
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="proc_grn_header",
            entity_id=grn.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return self.get_grn(ctx, grn.id)

    def confirm(self, ctx: TenantContext, grn_id: UUID):
        grn = self.get_grn(ctx, grn_id)
        order = self._orders.get_order_for_update(ctx, grn.order_header_id)
        if order is None:
            raise NotFoundException("Purchase order not found")
        order_lines_by_id = {ln.id: ln for ln in order.lines}
        self._engine.confirm_grn(grn, order, order_lines_by_id)
        self._inventory.receive_goods(
            ctx,
            grn_id=grn.id,
            order_id=order.id,
            warehouse_reference=grn.warehouse_reference,
        )
        self._db.flush()
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="proc_grn_header",
            entity_id=grn_id,
            operation="confirm",
            performed_by=ctx.user_id,
        )
        return grn
