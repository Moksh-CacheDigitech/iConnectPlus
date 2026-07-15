"""Connector lifecycle engine."""

from modules.integration.domain.enums import (
    ConnectorStatus,
)
from modules.integration.domain.exceptions import (
    InvalidConnectorState,
)


class ConnectorEngine:
    def submit(self, row) -> None:
        if row.status != ConnectorStatus.DRAFT.value:
            raise InvalidConnectorState("Only draft connectors can be submitted")
        row.status = ConnectorStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ConnectorStatus.SUBMITTED.value:
            raise InvalidConnectorState("Only submitted connectors can be approved")
        row.status = ConnectorStatus.APPROVED.value

    def activate(self, row) -> None:
        row.status = ConnectorStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ConnectorStatus.INACTIVE.value

    def mark_failed(self, row) -> None:
        row.status = ConnectorStatus.FAILED.value

    def retire(self, row) -> None:
        row.status = ConnectorStatus.RETIRED.value
