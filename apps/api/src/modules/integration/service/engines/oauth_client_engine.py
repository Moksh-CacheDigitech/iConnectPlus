"""OauthClient lifecycle engine."""

from modules.integration.domain.enums import (
    OauthClientStatus,
)


class OauthClientEngine:
    def activate(self, row) -> None:
        row.status = OauthClientStatus.ACTIVE.value

    def revoke(self, row) -> None:
        row.status = OauthClientStatus.REVOKED.value
