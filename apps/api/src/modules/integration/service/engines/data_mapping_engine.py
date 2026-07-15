"""DataMapping lifecycle engine."""

from modules.integration.domain.enums import (
    DataMappingStatus,
)


class DataMappingEngine:
    def activate(self, row) -> None:
        row.status = DataMappingStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = DataMappingStatus.INACTIVE.value
