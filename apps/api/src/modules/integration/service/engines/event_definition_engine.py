"""EventDefinition lifecycle engine."""

from modules.integration.domain.enums import (
    EventDefinitionStatus,
)


class EventDefinitionEngine:
    def activate(self, row) -> None:
        row.status = EventDefinitionStatus.ACTIVE.value
        row.is_active = True

    def deprecate(self, row) -> None:
        row.status = EventDefinitionStatus.DEPRECATED.value
        row.is_active = False
