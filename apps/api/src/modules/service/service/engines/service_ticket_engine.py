"""ServiceTicket lifecycle engine."""

from modules.service.domain.enums import (
    ServiceTicketStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceTicketState,
)


class ServiceTicketEngine:
    def start(self, row) -> None:
        if row.status not in {ServiceTicketStatus.OPEN.value, ServiceTicketStatus.PENDING.value}:
            raise InvalidServiceTicketState("Ticket not startable")
        row.status = ServiceTicketStatus.IN_PROGRESS.value

    def resolve(self, row) -> None:
        if row.status != ServiceTicketStatus.IN_PROGRESS.value:
            raise InvalidServiceTicketState("Only in-progress tickets can resolve")
        row.status = ServiceTicketStatus.RESOLVED.value

    def close(self, row) -> None:
        row.status = ServiceTicketStatus.CLOSED.value

    def cancel(self, row) -> None:
        row.status = ServiceTicketStatus.CANCELLED.value

