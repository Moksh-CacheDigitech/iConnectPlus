"""Production order lifecycle engine."""

from datetime import datetime, timezone
from decimal import Decimal

from modules.manufacturing.domain.enums import ProductionOrderStatus
from modules.manufacturing.domain.exceptions import InvalidProductionOrderState
from modules.manufacturing.models.production_order import MfgProductionOrder


class ProductionEngine:
    def validate_releasable(self, order: MfgProductionOrder) -> None:
        if order.status != ProductionOrderStatus.DRAFT.value:
            raise InvalidProductionOrderState("Only draft orders can be released")
        if Decimal(str(order.planned_qty)) <= 0:
            raise InvalidProductionOrderState("Planned qty must be positive")

    def validate_startable(self, order: MfgProductionOrder) -> None:
        if order.status != ProductionOrderStatus.RELEASED.value:
            raise InvalidProductionOrderState("Only released orders can start")

    def validate_completable(self, order: MfgProductionOrder) -> None:
        if order.status not in {
            ProductionOrderStatus.IN_PROGRESS.value,
            ProductionOrderStatus.RELEASED.value,
        }:
            raise InvalidProductionOrderState("Order cannot be completed from current status")

    def validate_closeable(self, order: MfgProductionOrder) -> None:
        if order.status != ProductionOrderStatus.COMPLETED.value:
            raise InvalidProductionOrderState("Only completed orders can be closed")

    def validate_cancellable(self, order: MfgProductionOrder) -> None:
        if order.status in {
            ProductionOrderStatus.CLOSED.value,
            ProductionOrderStatus.CANCELLED.value,
            ProductionOrderStatus.COMPLETED.value,
        }:
            raise InvalidProductionOrderState("Order cannot be cancelled")

    def apply_start(self, order: MfgProductionOrder) -> None:
        self.validate_startable(order)
        order.status = ProductionOrderStatus.IN_PROGRESS.value
        order.actual_start = datetime.now(timezone.utc)

    def apply_complete(self, order: MfgProductionOrder) -> None:
        self.validate_completable(order)
        order.status = ProductionOrderStatus.COMPLETED.value
        order.actual_end = datetime.now(timezone.utc)

    def apply_close(self, order: MfgProductionOrder) -> None:
        self.validate_closeable(order)
        order.status = ProductionOrderStatus.CLOSED.value

    def apply_cancel(self, order: MfgProductionOrder) -> None:
        self.validate_cancellable(order)
        order.status = ProductionOrderStatus.CANCELLED.value

    def apply_receipt_qty(self, order: MfgProductionOrder, qty: Decimal) -> None:
        if qty <= 0:
            raise InvalidProductionOrderState("Receipt qty must be positive")
        order.completed_qty = (Decimal(str(order.completed_qty or 0)) + qty).quantize(
            Decimal("0.0001")
        )
        if order.status == ProductionOrderStatus.RELEASED.value:
            order.status = ProductionOrderStatus.IN_PROGRESS.value
            if order.actual_start is None:
                order.actual_start = datetime.now(timezone.utc)

    def apply_scrap_qty(self, order: MfgProductionOrder, qty: Decimal) -> None:
        if qty < 0:
            raise InvalidProductionOrderState("Scrap qty cannot be negative")
        order.scrapped_qty = (Decimal(str(order.scrapped_qty or 0)) + qty).quantize(
            Decimal("0.0001")
        )
