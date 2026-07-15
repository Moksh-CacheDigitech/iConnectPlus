"""ServiceWorkOrder lifecycle engine."""

from modules.service.domain.enums import (
    ServiceWorkOrderStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceWorkOrderState,
)


class ServiceWorkOrderEngine:
    def submit(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.DRAFT.value:
            raise InvalidServiceWorkOrderState("Only draft work orders can be submitted")
        row.status = ServiceWorkOrderStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.SUBMITTED.value:
            raise InvalidServiceWorkOrderState("Only submitted work orders can be approved")
        row.status = ServiceWorkOrderStatus.APPROVED.value

    def assign(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.APPROVED.value:
            raise InvalidServiceWorkOrderState("Only approved work orders can be assigned")
        row.status = ServiceWorkOrderStatus.ASSIGNED.value

    def start(self, row) -> None:
        if row.status not in {ServiceWorkOrderStatus.APPROVED.value, ServiceWorkOrderStatus.ASSIGNED.value}:
            raise InvalidServiceWorkOrderState("Work order not startable")
        row.status = ServiceWorkOrderStatus.IN_PROGRESS.value

    def complete(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.IN_PROGRESS.value:
            raise InvalidServiceWorkOrderState("Only in-progress work orders can complete")
        row.status = ServiceWorkOrderStatus.COMPLETED.value

    def close(self, row) -> None:
        if row.status != ServiceWorkOrderStatus.COMPLETED.value:
            raise InvalidServiceWorkOrderState("Only completed work orders can close")
        row.status = ServiceWorkOrderStatus.CLOSED.value

    def cancel(self, row) -> None:
        row.status = ServiceWorkOrderStatus.CANCELLED.value

