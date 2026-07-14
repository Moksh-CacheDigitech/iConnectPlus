"""TaxConfiguration lifecycle engine."""

from modules.payroll.domain.enums import (
    TaxConfigurationStatus,
)
from modules.payroll.domain.exceptions import (
    InvalidTaxConfigurationState,
)


class TaxConfigurationEngine:
    def activate(self, row) -> None:
        if row.status != TaxConfigurationStatus.DRAFT.value:
            raise InvalidTaxConfigurationState("Only draft tax config can activate")
        row.status = TaxConfigurationStatus.ACTIVE.value

    def archive(self, row) -> None:
        if row.status != TaxConfigurationStatus.ACTIVE.value:
            raise InvalidTaxConfigurationState("Only active tax config can archive")
        row.status = TaxConfigurationStatus.ARCHIVED.value

