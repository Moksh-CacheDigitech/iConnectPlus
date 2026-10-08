"""Sales inventory adapters — reserve / issue / receive via platform port."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from modules.foundation.domain.value_objects import TenantContext
from modules.inventory.repository.reservation_repository import ReservationRepository
from modules.platform.adapters.inventory_adapter import InventoryStockAdapter
from modules.platform.dto import StockKey
from modules.platform.helpers.side_effects import enqueue_domain_event
from modules.sales.repository.delivery_repository import DeliveryRepository
from modules.sales.repository.order_repository import OrderRepository
from modules.sales.repository.return_repository import ReturnRepository


class SalesInventoryAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._stock = InventoryStockAdapter(db)
        self._orders = OrderRepository(db)
        self._deliveries = DeliveryRepository(db)
        self._returns = ReturnRepository(db)

    def reserve_order(self, ctx: TenantContext, order_id: UUID, warehouse_id: UUID) -> bool:
        order = self._orders.get_order(ctx, order_id)
        if order is None:
            return False
        for line in [ln for ln in order.lines if not ln.is_deleted]:
            self._stock.reserve(
                ctx,
                StockKey(
                    company_id=order.company_id,
                    branch_id=order.branch_id,
                    warehouse_id=warehouse_id,
                    product_id=line.product_id,
                    uom_id=line.uom_id,
                ),
                Decimal(str(line.quantity)),
                source_module="sales",
                source_document_type="sales_order",
                source_document_id=order.id,
                source_line_id=line.id,
            )
        return True

    def release_order(self, ctx: TenantContext, order_id: UUID) -> bool:
        reservations = ReservationRepository(self._db).list_by_source(
            ctx,
            source_module="sales",
            source_document_type="sales_order",
            source_document_id=order_id,
        )
        for res in reservations:
            if res.status in {"active", "partially_issued"}:
                self._stock.release(ctx, res.id)
        return True

    def issue_delivery(self, ctx: TenantContext, delivery_id: UUID) -> bool:
        delivery = self._deliveries.get_delivery(ctx, delivery_id)
        if delivery is None:
            return False
        warehouse_id = delivery.warehouse_reference
        if warehouse_id is None:
            return False
        reservations = ReservationRepository(self._db).list_by_source(
            ctx,
            source_module="sales",
            source_document_type="sales_order",
            source_document_id=delivery.order_header_id,
        )
        res_by_line = {r.source_line_id: r for r in reservations if r.source_line_id}
        for line in [ln for ln in delivery.lines if not ln.is_deleted]:
            reservation = res_by_line.get(line.order_line_id)
            self._stock.issue(
                ctx,
                StockKey(
                    company_id=delivery.company_id,
                    branch_id=delivery.branch_id,
                    warehouse_id=warehouse_id,
                    product_id=line.product_id,
                    uom_id=line.uom_id,
                ),
                Decimal(str(line.quantity)),
                source_module="sales",
                source_document_type="delivery",
                source_document_id=delivery.id,
                source_line_id=line.id,
                reservation_id=reservation.id if reservation else None,
            )
        enqueue_domain_event(
            self._db,
            tenant_id=ctx.tenant_id,
            event_type="domain.inventory.stock_issued",
            aggregate_type="delivery",
            aggregate_id=delivery_id,
            payload={"delivery_id": str(delivery_id)},
            idempotency_key=f"domain.inventory.stock_issued:delivery:{delivery_id}",
            created_by=ctx.user_id,
        )
        return True

    def receive_return(self, ctx: TenantContext, return_id: UUID, warehouse_id: UUID) -> bool:
        header = self._returns.get_return(ctx, return_id)
        if header is None:
            return False
        for line in [ln for ln in header.lines if not ln.is_deleted]:
            self._stock.receive(
                ctx,
                StockKey(
                    company_id=header.company_id,
                    branch_id=header.branch_id,
                    warehouse_id=warehouse_id,
                    product_id=line.product_id,
                    uom_id=line.uom_id,
                ),
                Decimal(str(line.quantity)),
                source_module="sales",
                source_document_type="sales_return",
                source_document_id=header.id,
                source_line_id=line.id,
                quality_status="quarantine",
            )
        enqueue_domain_event(
            self._db,
            tenant_id=ctx.tenant_id,
            event_type="domain.inventory.stock_received",
            aggregate_type="sales_return",
            aggregate_id=return_id,
            payload={"return_id": str(return_id)},
            idempotency_key=f"domain.inventory.stock_received:sales_return:{return_id}",
            created_by=ctx.user_id,
        )
        return True
