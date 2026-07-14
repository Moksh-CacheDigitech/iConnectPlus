"""ResourceAllocation lifecycle engine."""

from modules.project.domain.enums import (
    ResourceAllocationStatus,
)
from modules.project.domain.exceptions import (
    InvalidResourceAllocationState,
)


class ResourceAllocationEngine:
    def activate(self, row) -> None:
        if row.status != ResourceAllocationStatus.PLANNED.value:
            raise InvalidResourceAllocationState("Only planned allocations can activate")
        row.status = ResourceAllocationStatus.ACTIVE.value

    def complete(self, row) -> None:
        if row.status != ResourceAllocationStatus.ACTIVE.value:
            raise InvalidResourceAllocationState("Only active allocations can complete")
        row.status = ResourceAllocationStatus.COMPLETED.value

    def cancel(self, row) -> None:
        if row.status in {ResourceAllocationStatus.COMPLETED.value, ResourceAllocationStatus.CANCELLED.value}:
            raise InvalidResourceAllocationState("Allocation already terminal")
        row.status = ResourceAllocationStatus.CANCELLED.value

