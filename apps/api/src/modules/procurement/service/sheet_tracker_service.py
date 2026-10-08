"""Upload Excel trackers and merge new columns/rows into the extracted table."""

from __future__ import annotations

import base64
import binascii
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from core.exceptions import NotFoundException, ValidationException
from modules.foundation.domain.value_objects import TenantContext
from modules.platform.compat.audit_facade import PlatformAuditFacade
from modules.organization.repository.branch_repository import BranchRepository
from modules.procurement.repository.sheet_tracker_repository import SheetTrackerRepository
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator
from modules.procurement.service.sheet_tracker_grid import extract_sheet_table, merge_tracker_table
from shared.upload_safety import UnsafeUploadError, validate_upload

_MAX_BYTES = 12 * 1024 * 1024


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SheetTrackerService:
    def __init__(self, db: Session) -> None:
        self._repo = SheetTrackerRepository(db)
        self._scope = ProcurementScopeValidator(db)
        self._audit = PlatformAuditFacade(db)
        self._db = db

    def _company(self, ctx: TenantContext) -> UUID:
        cid = self._scope.resolve_company_id(ctx, None)
        if cid is None:
            raise ValidationException("Company context is required to store trackers")
        return cid

    def _branch(self, ctx: TenantContext, company_id: UUID) -> UUID:
        if ctx.branch_id is not None:
            return ctx.branch_id
        branches = BranchRepository(self._db).list_branches(ctx, company_id=company_id)
        if not branches:
            raise ValidationException("No branch is configured for this company")
        return branches[0].id

    def list(self, ctx: TenantContext):
        return self._repo.list_rows(ctx, self._scope.resolve_company_id(ctx, None))

    def get(self, ctx: TenantContext, tracker_id: UUID):
        row = self._repo.get(ctx, tracker_id)
        if row is None:
            raise NotFoundException("Tracker not found")
        return row

    def upload(
        self,
        ctx: TenantContext,
        *,
        file_name: str,
        content_base64: str,
        content_type: str | None = None,
        tracker_id: UUID | None = None,
        name: str | None = None,
    ):
        try:
            raw = base64.b64decode(content_base64, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValidationException("Invalid tracker file data") from exc
        try:
            safe_name, _media = validate_upload(
                file_name=file_name,
                content_type=content_type,
                raw=raw,
                max_bytes=_MAX_BYTES,
            )
        except UnsafeUploadError as exc:
            raise ValidationException(str(exc)) from exc
        ext = Path(safe_name).suffix.lower()
        if ext not in {".xlsx", ".xlsm", ".xls"}:
            raise ValidationException("Upload an Excel workbook (.xlsx)")

        incoming = extract_sheet_table(raw)
        cid = self._company(ctx)
        now = _utcnow()

        if tracker_id is None:
            title = (name or "").strip() or Path(safe_name).stem.replace("_", " ").strip() or "Tracker"
            row = self._repo.create(
                ctx,
                company_id=cid,
                branch_id=self._branch(ctx, cid),
                name=title[:180],
                last_file_name=safe_name,
                column_count=len(incoming["columns"]),
                row_count=len(incoming["rows"]),
                columns_json=incoming["columns"],
                rows_json=incoming["rows"],
                last_merge_json={
                    "added_columns": [c["label"] for c in incoming["columns"]],
                    "added_rows": len(incoming["rows"]),
                    "updated_rows": 0,
                    "file_name": safe_name,
                },
                last_upload_at=now,
            )
            self._audit.log_entity_change(
                tenant_id=ctx.tenant_id,
                entity_name="proc_sheet_tracker",
                entity_id=row.id,
                operation="create",
                performed_by=ctx.user_id,
            )
            return row

        row = self.get(ctx, tracker_id)
        merged = merge_tracker_table(list(row.columns_json or []), list(row.rows_json or []), incoming)
        row.columns_json = merged["columns"]
        row.rows_json = merged["rows"]
        row.column_count = len(merged["columns"])
        row.row_count = len(merged["rows"])
        row.last_file_name = safe_name
        row.last_upload_at = now
        row.last_merge_json = {
            "added_columns": merged["added_columns"],
            "added_rows": merged["added_rows"],
            "updated_rows": merged["updated_rows"],
            "file_name": safe_name,
        }
        if name and name.strip():
            row.name = name.strip()[:180]
        self._repo.save(ctx, row)
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="proc_sheet_tracker",
            entity_id=row.id,
            operation="update",
            performed_by=ctx.user_id,
        )
        return row
