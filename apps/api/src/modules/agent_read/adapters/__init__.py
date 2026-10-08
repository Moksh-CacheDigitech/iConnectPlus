"""Agent-read adapters — foreign ORM allowed here only."""

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
