"""ServiceMaterial lifecycle engine."""

from modules.service.domain.enums import (
    ServiceMaterialStatus,
)
from modules.service.domain.exceptions import (
    InvalidServiceMaterialState,
)


class ServiceMaterialEngine:
    def issue(self, row) -> None:
        if row.status != ServiceMaterialStatus.RESERVED.value:
            raise InvalidServiceMaterialState("Only reserved materials can be issued")
        row.status = ServiceMaterialStatus.ISSUED.value

    def return_material(self, row) -> None:
        if row.status != ServiceMaterialStatus.ISSUED.value:
            raise InvalidServiceMaterialState("Only issued materials can be returned")
        row.status = ServiceMaterialStatus.RETURNED.value

    def cancel(self, row) -> None:
        row.status = ServiceMaterialStatus.CANCELLED.value

