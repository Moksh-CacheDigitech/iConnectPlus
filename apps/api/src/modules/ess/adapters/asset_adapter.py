"""Asset read port for ESS workplace."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from modules.asset.models.asset import AstAsset
from modules.asset.models.asset_assignment import AstAssetAssignment
from modules.foundation.domain.value_objects import TenantContext


class EssAssetAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, asset_id: UUID) -> AstAsset | None:
        row = self._db.get(AstAsset, asset_id)
        if row is None or getattr(row, "is_deleted", False):
            return None
        return row

    def lookup_by_code(
        self, ctx: TenantContext, *, company_id: UUID, code: str
    ) -> AstAsset | None:
        raw = code.strip()
        if not raw:
            return None
        return self._db.scalar(
            select(AstAsset).where(
                AstAsset.tenant_id == ctx.tenant_id,
                AstAsset.company_id == company_id,
                AstAsset.is_deleted.is_(False),
                or_(
                    AstAsset.qr_code == raw,
                    AstAsset.asset_code == raw,
                    AstAsset.barcode == raw,
                ),
            )
        )

    def list_assigned_assets(
        self, *, employee_id: UUID
    ) -> list[tuple[AstAsset, AstAssetAssignment]]:
        assignments = list(
            self._db.scalars(
                select(AstAssetAssignment).where(
                    AstAssetAssignment.employee_id == employee_id,
                    AstAssetAssignment.is_deleted.is_(False),
                    AstAssetAssignment.status.in_(("active", "approved")),
                )
            ).all()
        )
        out: list[tuple[AstAsset, AstAssetAssignment]] = []
        for asn in assignments:
            asset = self.get(asn.asset_id)
            if asset is None:
                continue
            out.append((asset, asn))
        return out
