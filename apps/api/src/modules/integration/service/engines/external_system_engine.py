"""ExternalSystem lifecycle engine."""

from modules.integration.domain.enums import (
    ExternalSystemStatus,
)


class ExternalSystemEngine:
    def activate(self, row) -> None:
        row.status = ExternalSystemStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = ExternalSystemStatus.INACTIVE.value

    def retire(self, row) -> None:
        row.status = ExternalSystemStatus.RETIRED.value
