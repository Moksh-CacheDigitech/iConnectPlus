"""ServiceEscalation lifecycle engine."""

from modules.service.domain.enums import (
    ServiceEscalationStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceEscalationState,
)


class ServiceEscalationEngine:
    def escalate(self, row) -> None:
        if row.status != ServiceEscalationStatus.OPEN.value:
            raise InvalidServiceEscalationState("Only open escalations can escalate further")
        row.escalation_level = int(row.escalation_level or 1) + 1

    def acknowledge(self, row) -> None:
        if row.status != ServiceEscalationStatus.OPEN.value:
            raise InvalidServiceEscalationState("Only open escalations can be acknowledged")
        row.status = ServiceEscalationStatus.ACKNOWLEDGED.value

    def resolve(self, row) -> None:
        if row.status not in {ServiceEscalationStatus.OPEN.value, ServiceEscalationStatus.ACKNOWLEDGED.value}:
            raise InvalidServiceEscalationState("Escalation not resolvable")
        row.status = ServiceEscalationStatus.RESOLVED.value

    def cancel(self, row) -> None:
        row.status = ServiceEscalationStatus.CANCELLED.value

