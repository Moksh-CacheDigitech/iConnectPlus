"""Integration Hub gateway — external I/O only."""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID


class IIntegrationGateway(Protocol):
    def dispatch_outbound(
        self,
        *,
        tenant_id: UUID,
        system_code: str,
        operation: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> dict[str, Any]:
        """Queue or execute an outbound integration call via Integration Hub."""
        ...
