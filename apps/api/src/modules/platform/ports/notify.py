"""Notification port — modules emit intents; engine delivers."""

from __future__ import annotations

from typing import Any, Protocol

from modules.platform.dto import NotifyIntent


class INotify(Protocol):
    def publish(self, intent: NotifyIntent) -> Any:
        """Create notification event/delivery. Idempotent when idempotency_key set."""
        ...
