"""ServiceContract lifecycle engine."""

from modules.service.domain.enums import (
    ServiceContractStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceContractState,
)


class ServiceContractEngine:
    def submit(self, row) -> None:
        if row.status != ServiceContractStatus.DRAFT.value:
            raise InvalidServiceContractState("Only draft contracts can be submitted")
        row.status = ServiceContractStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ServiceContractStatus.SUBMITTED.value:
            raise InvalidServiceContractState("Only submitted contracts can be approved")
        row.status = ServiceContractStatus.APPROVED.value

    def activate(self, row) -> None:
        if row.status != ServiceContractStatus.APPROVED.value:
            raise InvalidServiceContractState("Only approved contracts can activate")
        row.status = ServiceContractStatus.ACTIVE.value

    def expire(self, row) -> None:
        row.status = ServiceContractStatus.EXPIRED.value

    def cancel(self, row) -> None:
        row.status = ServiceContractStatus.CANCELLED.value

