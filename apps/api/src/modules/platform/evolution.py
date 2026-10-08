"""Extraction / infra evolution readiness — not a microservices split.

Tier D items (K8s, OpenSearch, warehouse, service extract) stay gated until
these criteria are true for a bounded context.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractReadiness:
    context: str
    ports_adopted: bool
    outbox_adopted: bool
    orm_debt_cleared: bool
    slo_green: bool
    team_ownership: bool

    @property
    def ready(self) -> bool:
        return all(
            (
                self.ports_adopted,
                self.outbox_adopted,
                self.orm_debt_cleared,
                self.slo_green,
                self.team_ownership,
            )
        )


# Tracked contexts — update flags as migrations land.
EXTRACT_STATUS: dict[str, ExtractReadiness] = {
    "finance": ExtractReadiness("finance", True, True, True, False, False),
    "inventory": ExtractReadiness("inventory", True, True, True, False, False),
    "procurement": ExtractReadiness("procurement", True, True, True, False, False),
    "sales": ExtractReadiness("sales", True, True, True, False, False),
}

K8S_READY = False  # Compose/Coolify current; flip when HA + probes + IaC land
OPENSEARCH_READY = False
WAREHOUSE_READY = False  # Use AnaFinancePostingFact projections first
