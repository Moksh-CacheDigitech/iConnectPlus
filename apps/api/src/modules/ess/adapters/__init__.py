"""ESS cross-module adapters (no foreign ORM in ESS services)."""

from modules.ess.adapters.asset_adapter import EssAssetAdapter
from modules.ess.adapters.helpdesk_adapter import EssHelpdeskAdapter
from modules.ess.adapters.hr_adapter import EssHrAdapter

__all__ = ["EssAssetAdapter", "EssHelpdeskAdapter", "EssHrAdapter"]
