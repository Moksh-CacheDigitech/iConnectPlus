"""Agent-read adapters — foreign ORM allowed here only."""

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
