"""ApiUsage lifecycle engine."""

from modules.integration.domain.enums import (
    ApiUsageStatus,
)


class ApiUsageEngine:
    def record(self, row) -> None:
        row.status = ApiUsageStatus.RECORDED.value
