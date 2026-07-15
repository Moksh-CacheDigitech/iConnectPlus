"""Service domain entity markers."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class ServiceRequestIdentity:
    request_id: UUID
    document_number: str
    customer_id: UUID
