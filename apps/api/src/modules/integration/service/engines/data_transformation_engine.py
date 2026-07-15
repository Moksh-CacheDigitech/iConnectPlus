"""DataTransformation lifecycle engine."""

from modules.integration.domain.enums import (
    DataTransformationStatus,
)


class DataTransformationEngine:
    def activate(self, row) -> None:
        row.status = DataTransformationStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = DataTransformationStatus.INACTIVE.value
