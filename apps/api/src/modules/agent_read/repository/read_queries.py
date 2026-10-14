"""Re-export agent read repositories from adapters (foreign ORM lives there)."""

from modules.agent_read.adapters.read_queries import (
    AgentCustomerReadRepository,
    AgentLeadReadRepository,
    AgentProductReadRepository,
)

__all__ = [
    "AgentCustomerReadRepository",
    "AgentLeadReadRepository",
    "AgentProductReadRepository",
]
