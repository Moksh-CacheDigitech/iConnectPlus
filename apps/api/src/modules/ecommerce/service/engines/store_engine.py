"""Store lifecycle engine."""

from modules.ecommerce.domain.enums import (
    StoreStatus,
)
from modules.ecommerce.domain.exceptions import (
    InvalidStoreState,
)


class StoreEngine:
    def submit(self, row) -> None:
        if row.status != StoreStatus.DRAFT.value:
            raise InvalidStoreState("Only draft stores can be submitted")
        row.status = StoreStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != StoreStatus.SUBMITTED.value:
            raise InvalidStoreState("Only submitted stores can be approved")
        row.status = StoreStatus.APPROVED.value

    def activate(self, row) -> None:
        row.status = StoreStatus.ACTIVE.value

    def deactivate(self, row) -> None:
        row.status = StoreStatus.INACTIVE.value

    def retire(self, row) -> None:
        row.status = StoreStatus.RETIRED.value
