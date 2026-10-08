"""HR employee asset custody - list, assign, and return via asset assignments."""

from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import AppException, NotFoundException
from modules.asset.service.assignment_service import AssignmentService
from modules.foundation.domain.value_objects import TenantContext
from modules.hr.adapters.asset_port import HrAssetAdapter
from modules.hr.adapters.master_data_port import HrMasterDataAdapter

_RETURNABLE_STATUSES = ("approved", "active")


class EmployeeAssetService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._master = HrMasterDataAdapter(db)
        self._assets = HrAssetAdapter(db)
        self._assignments = AssignmentService(db)

    @staticmethod
    def _to_item(asset: Any, assignment: Any | None) -> dict:
        return {
            "id": asset.id,
            "assignment_id": assignment.id if assignment else None,
            "asset_code": asset.asset_code,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "serial_number": asset.serial_number,
            "asset_status": asset.status,
            "assignment_status": assignment.status if assignment else "custodian",
            "document_number": assignment.document_number if assignment else None,
            "allocated_at": assignment.allocated_at if assignment else None,
            "expected_return_at": assignment.expected_return_at if assignment else None,
            "returned_at": assignment.returned_at if assignment else None,
        }

    def list_for_employee(self, ctx: TenantContext, employee_id: UUID) -> list[dict]:
        self._master.get_employee(ctx, employee_id)
        items: list[dict] = []
        seen_assets: set[UUID] = set()
        for assignment in self._assets.list_employee_assignments(ctx.tenant_id, employee_id):
            asset = self._assets.get_asset(assignment.asset_id)
            if asset is None:
                continue
            seen_assets.add(asset.id)
            items.append(self._to_item(asset, assignment))

        for asset in self._assets.list_custodian_assets(ctx.tenant_id, employee_id):
            if asset.id in seen_assets:
                continue
            items.append(self._to_item(asset, None))
        return items

    def list_available_assets(
        self,
        ctx: TenantContext,
        employee_id: UUID,
        *,
        branch_id: UUID | None = None,
    ) -> list[dict]:
        self._master.get_employee(ctx, employee_id)
        available: list[dict] = []
        for asset in self._assets.list_active_assets(ctx.tenant_id, branch_id):
            if self._assets.has_active_assignment_for_other(asset.id, employee_id):
                continue
            if self._assets.active_assignment_for_employee(asset.id, employee_id):
                continue
            available.append(
                {
                    "id": asset.id,
                    "asset_code": asset.asset_code,
                    "asset_name": asset.asset_name,
                    "asset_type": asset.asset_type,
                    "serial_number": asset.serial_number,
                }
            )
        return available

    def assign(
        self,
        ctx: TenantContext,
        *,
        employee_id: UUID,
        asset_id: UUID,
        branch_id: UUID,
        expected_return_at: date | None = None,
    ) -> dict:
        self._master.get_employee(ctx, employee_id)
        asset = self._assets.get_asset(asset_id)
        if asset is None:
            raise NotFoundException("Asset not found")
        if self._assets.has_active_assignment_for_other(asset_id, employee_id):
            raise AppException("Asset is already assigned to another employee")
        if self._assets.active_assignment_for_employee(asset_id, employee_id):
            raise AppException("Asset is already assigned to this employee")

        allocated_at = datetime.now(timezone.utc)
        row = self._assignments.create(
            ctx,
            branch_id=branch_id,
            asset_id=asset_id,
            allocation_type="employee",
            employee_id=employee_id,
            department_id=asset.department_id,
            allocated_at=allocated_at,
            expected_return_at=expected_return_at,
            status="draft",
        )
        row = self._assignments.submit(ctx, row.id)
        row = self._assignments.approve(ctx, row.id)
        return self._to_item(asset, row)

    def return_asset(self, ctx: TenantContext, assignment_id: UUID) -> dict:
        row = self._assignments.get(ctx, assignment_id)
        if row.status not in _RETURNABLE_STATUSES:
            raise AppException("Only active assignments can be returned")
        updated = self._assignments.return_assignment(ctx, assignment_id)
        asset = self._assets.get_asset(updated.asset_id)
        if asset is None:
            raise NotFoundException("Asset not found")
        return self._to_item(asset, updated)
