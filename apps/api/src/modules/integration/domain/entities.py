"""Integration domain entity markers."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class ExternalSystemIdentity:
    system_id: UUID
    system_number: str
