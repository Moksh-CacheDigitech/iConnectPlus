"""Material return engine."""

from modules.manufacturing.domain.enums import MaterialDocStatus, ProductionOrderStatus
from modules.manufacturing.domain.exceptions import InvalidMaterialDocumentState
from modules.manufacturing.models.material_return import MfgMaterialReturn
from modules.manufacturing.models.production_order import MfgProductionOrder


class MaterialReturnEngine:
    def validate_confirmable(
        self, header: MfgMaterialReturn, order: MfgProductionOrder | None
    ) -> None:
        if header.status != MaterialDocStatus.DRAFT.value:
            raise InvalidMaterialDocumentState("Only draft returns can be confirmed")
        lines = [ln for ln in header.lines if not ln.is_deleted]
        if not lines:
            raise InvalidMaterialDocumentState("Return must have lines")
        if order is None:
            raise InvalidMaterialDocumentState("Production order required")
        if order.status in {
            ProductionOrderStatus.CLOSED.value,
            ProductionOrderStatus.CANCELLED.value,
        }:
            raise InvalidMaterialDocumentState("Order is closed or cancelled")
