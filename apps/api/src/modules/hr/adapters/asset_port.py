"""Asset read port for HR employee custody screens (writes go through AssignmentService)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.asset.models.asset import AstAsset
from modules.asset.models.asset_assignment import AstAssetAssignment

_ACTIVE_ASSIGNMENT_STATUSES = ("draft", "submitted", "approved", "active")


class HrAssetAdapter:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_asset(self, asset_id: UUID) -> AstAsset | None:
        asset = self._db.get(AstAsset, asset_id)
        if asset is None or getattr(asset, "is_deleted", False):
            return None
        return asset

    def has_active_assignment_for_other(self, asset_id: UUID, employee_id: UUID) -> bool:
        return (
            self._db.scalar(
                select(AstAssetAssignment.id).where(
                    AstAssetAssignment.asset_id == asset_id,
                    AstAssetAssignment.employee_id != employee_id,
                    AstAssetAssignment.is_deleted.is_(False),
                    AstAssetAssignment.status.in_(_ACTIVE_ASSIGNMENT_STATUSES),
                )
            )
            is not None
        )

    def active_assignment_for_employee(self, asset_id: UUID, employee_id: UUID):
        return self._db.scalar(
            select(AstAssetAssignment).where(
                AstAssetAssignment.asset_id == asset_id,
                AstAssetAssignment.employee_id == employee_id,
                AstAssetAssignment.is_deleted.is_(False),
                AstAssetAssignment.status.in_(("approved", "active")),
            )
        )

    def list_employee_assignments(self, tenant_id: UUID, employee_id: UUID) -> list:
        return list(
            self._db.scalars(
                select(AstAssetAssignment)
                .where(
                    AstAssetAssignment.tenant_id == tenant_id,
                    AstAssetAssignment.employee_id == employee_id,
                    AstAssetAssignment.is_deleted.is_(False),
                )
                .order_by(AstAssetAssignment.allocated_at.desc().nullslast())
            ).all()
        )

    def list_custodian_assets(self, tenant_id: UUID, employee_id: UUID) -> list[AstAsset]:
        return list(
            self._db.scalars(
                select(AstAsset).where(
                    AstAsset.tenant_id == tenant_id,
                    AstAsset.custodian_employee_id == employee_id,
                    AstAsset.is_deleted.is_(False),
                )
            ).all()
        )

    def list_active_assets(self, tenant_id: UUID, branch_id: UUID | None) -> list[AstAsset]:
        stmt = select(AstAsset).where(
            AstAsset.tenant_id == tenant_id,
            AstAsset.is_deleted.is_(False),
            AstAsset.status == "active",
        )
        if branch_id is not None:
            stmt = stmt.where(AstAsset.branch_id == branch_id)
        return list(self._db.scalars(stmt.order_by(AstAsset.asset_code)).all())
