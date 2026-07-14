"""Routing engine."""

from decimal import Decimal

from modules.manufacturing.domain.entities import OperationTemplate
from modules.manufacturing.domain.enums import LineStatus, RoutingStatus
from modules.manufacturing.domain.exceptions import InvalidRoutingState
from modules.manufacturing.models.routing import MfgRouting


class RoutingEngine:
    def validate_activatable(self, routing: MfgRouting) -> None:
        if routing.status != RoutingStatus.DRAFT.value:
            raise InvalidRoutingState("Only draft routings can be activated")
        ops = [
            op
            for op in routing.operations
            if not op.is_deleted and op.status == LineStatus.ACTIVE.value
        ]
        if not ops:
            raise InvalidRoutingState("Routing needs at least one active operation")

    def build_operations(
        self, routing: MfgRouting, planned_qty: Decimal
    ) -> list[OperationTemplate]:
        if planned_qty <= 0:
            raise InvalidRoutingState("Planned quantity must be positive")
        templates: list[OperationTemplate] = []
        for op in sorted(routing.operations, key=lambda o: o.operation_seq):
            if op.is_deleted or op.status != LineStatus.ACTIVE.value:
                continue
            templates.append(
                OperationTemplate(
                    operation_seq=int(op.operation_seq),
                    operation_code=op.operation_code,
                    operation_name=op.operation_name,
                    work_center_id=op.work_center_id,
                    setup_time_minutes=Decimal(str(op.setup_time_minutes or 0)),
                    run_time_minutes=Decimal(str(op.run_time_minutes or 0)),
                    routing_operation_id=op.id,
                )
            )
        return templates
