"""Asset domain entity markers."""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class AssetIdentity:
    asset_id: UUID
    master_asset_id: UUID | None
    asset_code: str
