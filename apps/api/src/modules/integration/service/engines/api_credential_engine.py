"""ApiCredential lifecycle engine."""

from modules.integration.domain.enums import (
    ApiCredentialStatus,
)
from modules.integration.domain.exceptions import (
    InvalidApiCredentialState,
)


class ApiCredentialEngine:
    def submit(self, row) -> None:
        if row.status != ApiCredentialStatus.DRAFT.value:
            raise InvalidApiCredentialState("Only draft credentials can be submitted")
        row.status = ApiCredentialStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != ApiCredentialStatus.SUBMITTED.value:
            raise InvalidApiCredentialState("Only submitted credentials can be approved")
        row.status = ApiCredentialStatus.APPROVED.value

    def activate(self, row) -> None:
        row.status = ApiCredentialStatus.ACTIVE.value

    def revoke(self, row) -> None:
        row.status = ApiCredentialStatus.REVOKED.value

    def expire(self, row) -> None:
        row.status = ApiCredentialStatus.EXPIRED.value
