"""Webhook lifecycle engine."""

from modules.integration.domain.enums import (
    WebhookStatus,
)
from modules.integration.domain.exceptions import (
    InvalidWebhookState,
)


class WebhookEngine:
    def submit(self, row) -> None:
        if row.status != WebhookStatus.DRAFT.value:
            raise InvalidWebhookState("Only draft webhooks can be submitted")
        row.status = WebhookStatus.SUBMITTED.value

    def approve(self, row) -> None:
        if row.status != WebhookStatus.SUBMITTED.value:
            raise InvalidWebhookState("Only submitted webhooks can be approved")
        row.status = WebhookStatus.APPROVED.value

    def activate(self, row) -> None:
        row.status = WebhookStatus.ACTIVE.value
        row.is_enabled = True

    def pause(self, row) -> None:
        row.status = WebhookStatus.PAUSED.value
        row.is_enabled = False

    def retire(self, row) -> None:
        row.status = WebhookStatus.RETIRED.value
        row.is_enabled = False
