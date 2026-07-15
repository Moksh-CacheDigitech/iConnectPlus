"""E-Commerce domain entity markers."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class StoreIdentity:
    store_id: UUID
    store_number: str
