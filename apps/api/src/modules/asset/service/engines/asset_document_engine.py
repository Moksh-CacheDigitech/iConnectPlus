"""AssetDocument lifecycle engine."""

from modules.asset.domain.enums import (
    AssetDocumentStatus,
)


class AssetDocumentEngine:
    def supersede(self, row) -> None:
        row.status = AssetDocumentStatus.SUPERSEDED.value

    def archive(self, row) -> None:
        row.status = AssetDocumentStatus.ARCHIVED.value

