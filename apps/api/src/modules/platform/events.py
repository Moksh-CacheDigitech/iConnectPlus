"""Selective domain event type registry (outbox → RabbitMQ maturity path)."""

from __future__ import annotations

# High-value domain events only — not bus-everywhere.
DOMAIN_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "domain.finance.journal_posted",
        "domain.inventory.stock_received",
        "domain.inventory.stock_issued",
        "domain.procurement.po_approved",
        "domain.sales.order_confirmed",
        "domain.hr.employee_separated",
        "domain.payroll.run_finalized",
        "domain.asset.disposed",
    }
)


def is_registered_domain_event(event_type: str) -> bool:
    return event_type in DOMAIN_EVENT_TYPES
