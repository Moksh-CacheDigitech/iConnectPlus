"""ServiceRequest lifecycle engine."""

from modules.service.domain.enums import (
    ServiceRequestStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceRequestState,
)


class ServiceRequestEngine:
    def submit(self, row) -> None:
        if row.status != ServiceRequestStatus.DRAFT.value:
            raise InvalidServiceRequestState("Only draft requests can be submitted")
        row.status = ServiceRequestStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceRequestStatus.SUBMITTED.value:
            raise InvalidServiceRequestState("Only submitted requests can be approved")
        row.status = ServiceRequestStatus.APPROVED.value

    def assign(self, row) -> None:
        if row.status not in {ServiceRequestStatus.APPROVED.value, ServiceRequestStatus.NEW.value}:
            raise InvalidServiceRequestState("Request not assignable")
        row.status = ServiceRequestStatus.ASSIGNED.value

    def start(self, row) -> None:
        if row.status != ServiceRequestStatus.ASSIGNED.value:
            raise InvalidServiceRequestState("Only assigned requests can start")
        row.status = ServiceRequestStatus.IN_PROGRESS.value

    def resolve(self, row) -> None:
        if row.status != ServiceRequestStatus.IN_PROGRESS.value:
            raise InvalidServiceRequestState("Only in-progress requests can resolve")
        row.status = ServiceRequestStatus.RESOLVED.value

    def close(self, row) -> None:
        if row.status != ServiceRequestStatus.RESOLVED.value:
            raise InvalidServiceRequestState("Only resolved requests can close")
        row.status = ServiceRequestStatus.CLOSED.value

    def cancel(self, row) -> None:
        if row.status in {ServiceRequestStatus.CLOSED.value, ServiceRequestStatus.CANCELLED.value}:
            raise InvalidServiceRequestState("Request already terminal")
        row.status = ServiceRequestStatus.CANCELLED.value

