"""Monitor lifecycle engine."""

from modules.integration.domain.enums import (
    MonitorStatus,
)


class MonitorEngine:
    def mark_healthy(self, row) -> None:
        row.status = MonitorStatus.HEALTHY.value
        row.last_status = MonitorStatus.HEALTHY.value

    def mark_degraded(self, row) -> None:
        row.status = MonitorStatus.DEGRADED.value
        row.last_status = MonitorStatus.DEGRADED.value

    def mark_down(self, row) -> None:
        row.status = MonitorStatus.DOWN.value
        row.last_status = MonitorStatus.DOWN.value

    def deactivate(self, row) -> None:
        row.status = MonitorStatus.INACTIVE.value
