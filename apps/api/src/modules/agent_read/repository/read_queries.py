"""Re-export agent read repositories from adapters (foreign ORM lives there)."""

from modules.agent_read.adapters.read_queries import (
    AgentCustomerReadRepository,
    AgentInvoiceReadRepository,
    AgentLeadReadRepository,
    AgentOrderReadRepository,
    AgentProductReadRepository,
)

__all__ = [
    "AgentCustomerReadRepository",
    "AgentInvoiceReadRepository",
    "AgentLeadReadRepository",
    "AgentOrderReadRepository",
    "AgentProductReadRepository",
]
