"""Asset value objects."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DepreciationAmount:
    amount: Decimal
    book_value_after: Decimal


@dataclass(frozen=True)
class AssetCodes:
    asset_code: str
    document_number: str
