"""Material issue engine."""

from modules.manufacturing.domain.enums import MaterialDocStatus, ProductionOrderStatus
from modules.manufacturing.domain.exceptions import InvalidMaterialDocumentState
from modules.manufacturing.models.material_issue import MfgMaterialIssue
from modules.manufacturing.models.production_order import MfgProductionOrder


class MaterialIssueEngine:
    def validate_confirmable(
        self, header: MfgMaterialIssue, order: MfgProductionOrder | None
    ) -> None:
        if header.status != MaterialDocStatus.DRAFT.value:
            raise InvalidMaterialDocumentState("Only draft issues can be confirmed")
        lines = [ln for ln in header.lines if not ln.is_deleted]
        if not lines:
            raise InvalidMaterialDocumentState("Issue must have lines")
        if order is None:
            raise InvalidMaterialDocumentState("Production order required")
        if order.status not in {
            ProductionOrderStatus.RELEASED.value,
            ProductionOrderStatus.IN_PROGRESS.value,
        }:
            raise InvalidMaterialDocumentState("Order must be released or in progress")
