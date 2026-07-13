"""Journal and GL routers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.finance.dependencies import PaginationParams, get_pagination, paginate
from modules.finance.schemas import (
    GlEntryResponse,
    JournalCreateRequest,
    JournalLineCreateRequest,
    JournalLineResponse,
    JournalResponse,
    WorkflowActionRequest,
)
from modules.finance.service.general_ledger_service import GeneralLedgerService
from modules.finance.service.journal_service import JournalService
from modules.finance.service.posting_service import PostingService
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from shared.schemas import APIResponse

journals_router = APIRouter(prefix="/journals", tags=["Finance - Journals"])
gl_router = APIRouter(prefix="/gl", tags=["Finance - General Ledger"])


@journals_router.get("", response_model=APIResponse[list[JournalResponse]])
def list_journals(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.journal:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
) -> APIResponse[list[JournalResponse]]:
    journals = JournalService(db).list_journals(ctx, company_id)
    page = paginate(journals, pagination)
    return APIResponse(
        message="Journals retrieved",
        data=[JournalResponse.model_validate(j) for j in page],
    )


@journals_router.post("", response_model=APIResponse[JournalResponse])
def create_journal(
    body: JournalCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.journal:create"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[JournalResponse]:
    journal = JournalService(db).create_journal(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Journal created", data=JournalResponse.model_validate(journal))


@journals_router.get("/{journal_id}", response_model=APIResponse[JournalResponse])
def get_journal(
    journal_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.journal:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[JournalResponse]:
    journal = JournalService(db).get_journal(ctx, journal_id)
    return APIResponse(message="Journal retrieved", data=JournalResponse.model_validate(journal))


@journals_router.post("/{journal_id}/lines", response_model=APIResponse[JournalLineResponse])
def add_journal_line(
    journal_id: UUID,
    body: JournalLineCreateRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.journal:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[JournalLineResponse]:
    line = JournalService(db).add_line(ctx, journal_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Journal line added", data=JournalLineResponse.model_validate(line))


@journals_router.post("/{journal_id}/submit", response_model=APIResponse[dict])
def submit_journal(
    journal_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.journal:submit"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = JournalService(db).submit(ctx, journal_id)
    db.commit()
    return APIResponse(message="Journal submitted", data={"workflow_instance_id": str(instance.id)})


@journals_router.post("/{journal_id}/approve", response_model=APIResponse[dict])
def approve_journal(
    journal_id: UUID,
    _body: WorkflowActionRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.journal:approve"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    instance = JournalService(db).approve(ctx, journal_id)
    db.commit()
    return APIResponse(message="Journal approved", data={"status": instance.status})


@journals_router.post("/{journal_id}/post", response_model=APIResponse[list[GlEntryResponse]])
def post_journal(
    journal_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.journal:post"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list[GlEntryResponse]]:
    entries = PostingService(db).post_journal(ctx, journal_id)
    db.commit()
    return APIResponse(
        message="Journal posted",
        data=[GlEntryResponse.model_validate(e) for e in entries],
    )


@journals_router.post("/{journal_id}/reverse", response_model=APIResponse[JournalResponse])
def reverse_journal(
    journal_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("finance.journal:reverse"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[JournalResponse]:
    reversal = JournalService(db).reverse(ctx, journal_id)
    db.commit()
    return APIResponse(message="Reversal journal created", data=JournalResponse.model_validate(reversal))


@gl_router.get("", response_model=APIResponse[list[GlEntryResponse]])
def list_gl_entries(
    ctx: Annotated[TenantContext, Depends(require_permission("finance.gl:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
    account_id: UUID | None = None,
    period_id: UUID | None = None,
) -> APIResponse[list[GlEntryResponse]]:
    entries = GeneralLedgerService(db).list_entries(
        ctx, company_id, account_id=account_id, period_id=period_id
    )
    page = paginate(entries, pagination)
    return APIResponse(
        message="GL entries retrieved",
        data=[GlEntryResponse.model_validate(e) for e in page],
    )
