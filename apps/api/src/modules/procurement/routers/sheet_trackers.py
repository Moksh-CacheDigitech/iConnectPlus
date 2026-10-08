"""Excel tracker upload: merge new rows and columns into the extracted table."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.schemas import (
    SheetTrackerColumn,
    SheetTrackerDetailResponse,
    SheetTrackerMergeInfo,
    SheetTrackerSummaryResponse,
    SheetTrackerUploadRequest,
)
from modules.procurement.service.sheet_tracker_service import SheetTrackerService
from shared.schemas import APIResponse

sheet_tracker_router = APIRouter(prefix="/scm", tags=["Procurement - Sheet trackers"])

_READ = require_permission("procurement.order:read")
_WRITE = require_permission("procurement.order:create")


def _merge_info(row) -> SheetTrackerMergeInfo | None:
    raw = row.last_merge_json
    if not isinstance(raw, dict):
        return None
    return SheetTrackerMergeInfo(
        added_columns=[str(x) for x in (raw.get("added_columns") or [])],
        added_rows=int(raw.get("added_rows") or 0),
        updated_rows=int(raw.get("updated_rows") or 0),
        file_name=str(raw["file_name"]) if raw.get("file_name") else None,
    )


def _summary(row) -> SheetTrackerSummaryResponse:
    return SheetTrackerSummaryResponse(
        id=row.id,
        name=row.name,
        last_file_name=row.last_file_name,
        column_count=row.column_count,
        row_count=row.row_count,
        last_upload_at=row.last_upload_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
        version=row.version,
        last_merge=_merge_info(row),
    )


def _detail(row) -> SheetTrackerDetailResponse:
    columns = [
        SheetTrackerColumn(id=str(c.get("id")), label=str(c.get("label")))
        for c in (row.columns_json or [])
        if isinstance(c, dict) and c.get("id") and c.get("label")
    ]
    rows: list[dict[str, str]] = []
    for raw in row.rows_json or []:
        if not isinstance(raw, dict):
            continue
        rows.append({str(k): "" if v is None else str(v) for k, v in raw.items()})
    base = _summary(row)
    return SheetTrackerDetailResponse(
        **base.model_dump(),
        columns=columns,
        rows=rows,
    )


@sheet_tracker_router.get("/sheet-trackers", response_model=APIResponse[list[SheetTrackerSummaryResponse]])
def list_sheet_trackers(
    ctx: Annotated[TenantContext, Depends(_READ)],
    db: Annotated[Session, Depends(get_db)],
):
    rows = SheetTrackerService(db).list(ctx)
    return APIResponse(message="OK", data=[_summary(r) for r in rows])


@sheet_tracker_router.get("/sheet-trackers/{tracker_id}", response_model=APIResponse[SheetTrackerDetailResponse])
def get_sheet_tracker(
    tracker_id: UUID,
    ctx: Annotated[TenantContext, Depends(_READ)],
    db: Annotated[Session, Depends(get_db)],
):
    row = SheetTrackerService(db).get(ctx, tracker_id)
    return APIResponse(message="OK", data=_detail(row))


@sheet_tracker_router.post("/sheet-trackers", response_model=APIResponse[SheetTrackerDetailResponse])
def upload_sheet_tracker(
    body: SheetTrackerUploadRequest,
    ctx: Annotated[TenantContext, Depends(_WRITE)],
    db: Annotated[Session, Depends(get_db)],
):
    row = SheetTrackerService(db).upload(ctx, **body.model_dump())
    db.commit()
    message = "Tracker table created" if body.tracker_id is None else "Tracker table updated"
    return APIResponse(message=message, data=_detail(row))
