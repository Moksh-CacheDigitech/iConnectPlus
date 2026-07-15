"""Shipment lifecycle engine."""

from modules.ecommerce.domain.enums import (
    ShipmentStatus,
)


class ShipmentEngine:
    def pack(self, row) -> None:
        row.status = ShipmentStatus.PACKED.value

    def ship(self, row) -> None:
        row.status = ShipmentStatus.SHIPPED.value

    def deliver(self, row) -> None:
        row.status = ShipmentStatus.DELIVERED.value

    def cancel(self, row) -> None:
        row.status = ShipmentStatus.CANCELLED.value
