"""Delivery service."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.service.audit_service import AuditService
from modules.inventory.adapters.sales_adapter import SalesInventoryAdapter
from modules.sales.domain.enums import DeliveryStatus, SalesEntityType
from modules.sales.models.delivery import SalesDeliveryHeader
from modules.sales.repository.delivery_repository import DeliveryRepository
from modules.sales.repository.order_repository import OrderRepository
from modules.sales.service.document_number_service import DocumentNumberService
from modules.sales.service.engines.delivery_engine import DeliveryEngine
from modules.sales.service.sales_scope_validator import SalesScopeValidator


class DeliveryService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = DeliveryRepository(db)
        self._orders = OrderRepository(db)
        self._scope = SalesScopeValidator(db)
        self._engine = DeliveryEngine()
        self._numbers = DocumentNumberService(db)
        self._inventory = SalesInventoryAdapter(db)
        self._audit = AuditService(db)

    def list_deliveries(self, ctx: TenantContext, company_id: UUID | None = None):
        cid = self._scope.resolve_company_id(ctx, company_id)
        return self._repo.list_deliveries(ctx, cid)

    def get_delivery(self, ctx: TenantContext, delivery_id: UUID) -> SalesDeliveryHeader:
        row = self._repo.get_delivery(ctx, delivery_id)
        if row is None:
            raise NotFoundException("Delivery not found")
        self._scope.validate_company_access(ctx, row.company_id)
        self._scope.validate_branch_access(ctx, row.branch_id)
        return row

    def create_from_order(
        self,
        ctx: TenantContext,
        *,
        order_header_id: UUID,
        document_date,
        ship_to_address: str | None = None,
        warehouse_reference: UUID | None = None,
        company_id: UUID | None = None,
        lines: list[dict] | None = None,
    ):
        order = self._orders.get_order(ctx, order_header_id)
        if order is None:
            raise NotFoundException("Sales order not found")
        self._scope.validate_company_access(ctx, order.company_id)
        self._scope.validate_branch_access(ctx, order.branch_id)
        self._engine.validate_order_for_delivery(order)
        cid = self._scope.resolve_company_id(ctx, company_id or order.company_id)
        doc_number = self._numbers.generate(
            SalesEntityType.DELIVERY,
            cid,
            model=SalesDeliveryHeader,
            code_column="document_number",
        )
        delivery = self._repo.create_delivery(
            ctx,
            company_id=cid,
            branch_id=order.branch_id,
            document_number=doc_number,
            document_date=document_date,
            order_header_id=order.id,
            customer_id=order.customer_id,
            ship_to_address=ship_to_address,
            warehouse_reference=warehouse_reference,
            status=DeliveryStatus.DRAFT.value,
        )
        if lines:
            for spec in lines:
                order_line = next(
                    (ln for ln in order.lines if ln.id == spec["order_line_id"]), None
                )
                if order_line is None:
                    raise NotFoundException("Order line not found")
                qty = Decimal(str(spec["quantity"]))
                self._engine.validate_delivery_qty(order_line, qty)
                self._repo.add_line(
                    ctx,
                    delivery,
                    order_line_id=order_line.id,
                    line_number=spec["line_number"],
                    product_id=order_line.product_id,
                    quantity=float(qty),
                    uom_id=order_line.uom_id,
                    batch_reference=spec.get("batch_reference"),
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
                    delivery,
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
            entity_name="sales_delivery_header",
            entity_id=delivery.id,
            operation="create",
            performed_by=ctx.user_id,
        )
        return self.get_delivery(ctx, delivery.id)

    def ship(self, ctx: TenantContext, delivery_id: UUID):
        delivery = self.get_delivery(ctx, delivery_id)
        order = self._orders.get_order_for_update(ctx, delivery.order_header_id)
        if order is None:
            raise NotFoundException("Sales order not found")
        order_lines_by_id = {ln.id: ln for ln in order.lines}
        self._engine.confirm_delivery(delivery, order, order_lines_by_id)
        if delivery.warehouse_reference is not None:
            self._inventory.issue_delivery(ctx, delivery_id)
        delivery.shipped_at = datetime.now(timezone.utc)
        delivery.shipped_by = ctx.user_id
        self._db.flush()
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="sales_delivery_header",
            entity_id=delivery_id,
            operation="ship",
            performed_by=ctx.user_id,
        )
        return delivery
