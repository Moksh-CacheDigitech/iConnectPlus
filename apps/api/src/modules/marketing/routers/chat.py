"""Marketing Chat sessions + OpenAI multimodal message API."""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from modules.marketing.dependencies import TenantContext, get_db, require_permission
from modules.marketing.models.chat_session import MktChatAttachment, MktChatMessage, MktChatSession
from modules.marketing.service.chat_service import ChatService
from shared.schemas import APIResponse

chat_router = APIRouter(prefix="/chat", tags=["Marketing - Chat"])


class ChatSettingsPayload(BaseModel):
    provider: str | None = None
    model: str | None = None
    temperature: float | None = None
    maxTokens: int | None = None
    systemPrompt: str | None = None
    ragEnabled: bool | None = None
    ragSource: str | None = None
    ragTopK: int | None = None
    ragMinScore: float | None = None
    ragIndexHint: str | None = None
    brandKitEnabled: bool | None = None
    brandKitIncludeVoice: bool | None = None
    brandKitIncludeColors: bool | None = None
    brandKitIncludeLogoRules: bool | None = None
    brandKitVoiceId: str | None = None


class ChatSessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    settings: ChatSettingsPayload | None = None
    company_id: UUID | None = None


class ChatSessionRename(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ChatMessageCreate(BaseModel):
    content: str = Field(default="", max_length=16000)
    settings: ChatSettingsPayload | None = None
    attachment_ids: list[UUID] = Field(default_factory=list)
    generate_image: bool | None = None
    image_size: str | None = None
    image_quality: str | None = None


class ChatFromImagePost(BaseModel):
    content_id: UUID
    settings: ChatSettingsPayload | None = None


class ChatAttachmentOut(BaseModel):
    id: UUID
    session_id: UUID
    message_id: UUID | None = None
    kind: str
    status: str
    filename: str
    content_type: str
    size_bytes: int
    created_at: str | None = None


class ChatSessionOut(BaseModel):
    id: UUID
    title: str
    status: str
    message_count: int
    last_message_at: str | None = None
    last_model: str | None = None
    settings_json: dict[str, Any] | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ChatMessageOut(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    sequence_no: int
    model: str | None = None
    usage_json: dict[str, Any] | None = None
    meta_json: dict[str, Any] | None = None
    attachments: list[ChatAttachmentOut] = Field(default_factory=list)
    created_at: str | None = None


class ChatSendResult(BaseModel):
    session: ChatSessionOut
    user_message: ChatMessageOut
    assistant_message: ChatMessageOut


class ChatFromImagePostResult(BaseModel):
    session: ChatSessionOut
    attachment: ChatAttachmentOut
    suggested_prompt: str | None = None


def _iso(value) -> str | None:
    if value is None:
        return None
    try:
        return value.isoformat()
    except Exception:
        return str(value)


def _session_out(row: MktChatSession) -> ChatSessionOut:
    return ChatSessionOut(
        id=row.id,
        title=row.title,
        status=row.status,
        message_count=int(row.message_count or 0),
        last_message_at=_iso(row.last_message_at),
        last_model=row.last_model,
        settings_json=row.settings_json if isinstance(row.settings_json, dict) else None,
        created_at=_iso(getattr(row, "created_at", None)),
        updated_at=_iso(getattr(row, "updated_at", None)),
    )


def _attachment_out(row: MktChatAttachment) -> ChatAttachmentOut:
    return ChatAttachmentOut(
        id=row.id,
        session_id=row.session_id,
        message_id=row.message_id,
        kind=row.kind,
        status=row.status,
        filename=row.filename,
        content_type=row.content_type,
        size_bytes=int(row.size_bytes or 0),
        created_at=_iso(getattr(row, "created_at", None)),
    )


def _message_out(
    row: MktChatMessage, attachments: list[MktChatAttachment] | None = None
) -> ChatMessageOut:
    return ChatMessageOut(
        id=row.id,
        session_id=row.session_id,
        role=row.role,
        content=row.content,
        sequence_no=int(row.sequence_no or 0),
        model=row.model,
        usage_json=row.usage_json if isinstance(row.usage_json, dict) else None,
        meta_json=row.meta_json if isinstance(row.meta_json, dict) else None,
        attachments=[_attachment_out(a) for a in (attachments or [])],
        created_at=_iso(getattr(row, "created_at", None)),
    )


class ChatSpendBucket(BaseModel):
    usd: float
    tokens: int
    message_count: int


class ChatSpendLast(BaseModel):
    message_id: str | None = None
    session_id: str | None = None
    created_at: str | None = None
    usd: float = 0.0
    tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    source: str | None = None
    model: str | None = None
    kind: str | None = None


class ChatSpendFx(BaseModel):
    usd_inr: float
    as_of: str | None = None
    source: str = "frankfurter"
    provider: str = "frankfurter"
    provider_url: str | None = None


class ChatSpendSummary(BaseModel):
    currency: str = "USD"
    today: ChatSpendBucket
    last_7_days: ChatSpendBucket
    last_reply: ChatSpendLast
    rates: dict[str, float]
    fx: ChatSpendFx | None = None


@chat_router.get("/providers", response_model=APIResponse[dict])
def chat_providers(
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ChatService(db).provider_status())


@chat_router.get("/usage", response_model=APIResponse[ChatSpendSummary])
def chat_usage(
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
    refresh_fx: bool = False,
):
    data = ChatService(db).usage_summary(ctx, company_id, refresh_fx=refresh_fx)
    return APIResponse(message="OK", data=data)


@chat_router.get("/sessions", response_model=APIResponse[list[ChatSessionOut]])
def list_chat_sessions(
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
):
    rows = ChatService(db).list_sessions(ctx, company_id)
    return APIResponse(message="OK", data=[_session_out(r) for r in rows])


@chat_router.post("/sessions", response_model=APIResponse[ChatSessionOut])
def create_chat_session(
    body: ChatSessionCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:generate"))],
    db: Annotated[Session, Depends(get_db)],
):
    settings = body.settings.model_dump(exclude_none=True) if body.settings else None
    row = ChatService(db).create_session(
        ctx,
        title=body.title,
        settings=settings,
        company_id=body.company_id,
    )
    db.commit()
    db.refresh(row)
    return APIResponse(message="OK", data=_session_out(row))


@chat_router.get("/sessions/{session_id}", response_model=APIResponse[ChatSessionOut])
def get_chat_session(
    session_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ChatService(db).get_session(ctx, session_id)
    return APIResponse(message="OK", data=_session_out(row))


@chat_router.patch("/sessions/{session_id}", response_model=APIResponse[ChatSessionOut])
def rename_chat_session(
    session_id: UUID,
    body: ChatSessionRename,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:generate"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ChatService(db).rename_session(ctx, session_id, body.title)
    db.commit()
    db.refresh(row)
    return APIResponse(message="OK", data=_session_out(row))


@chat_router.delete("/sessions/{session_id}", response_model=APIResponse[None])
def delete_chat_session(
    session_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:generate"))],
    db: Annotated[Session, Depends(get_db)],
):
    ChatService(db).archive_session(ctx, session_id)
    db.commit()
    return APIResponse(message="OK", data=None)


@chat_router.post(
    "/from-image-post",
    response_model=APIResponse[ChatFromImagePostResult],
)
def start_chat_from_image_post(
    body: ChatFromImagePost,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:generate"))],
    db: Annotated[Session, Depends(get_db)],
):
    settings = body.settings.model_dump(exclude_none=True) if body.settings else None
    session, attachment = ChatService(db).start_from_image_post(
        ctx,
        body.content_id,
        settings=settings,
    )
    db.commit()
    db.refresh(session)
    db.refresh(attachment)
    meta = attachment.meta_json if isinstance(attachment.meta_json, dict) else {}
    prompt = str(meta.get("prompt") or "").strip()
    suggested = (
        "Help me refine this marketing creative. Suggest copy/layout improvements, "
        "or edit the image based on my next instruction."
    )
    if prompt:
        suggested = (
            f"This image was generated from: “{prompt[:280]}”. "
            "Help me refine it — suggest copy/layout changes or edit the image."
        )
    return APIResponse(
        message="OK",
        data=ChatFromImagePostResult(
            session=_session_out(session),
            attachment=_attachment_out(attachment),
            suggested_prompt=suggested,
        ),
    )


@chat_router.post(
    "/sessions/{session_id}/attachments",
    response_model=APIResponse[ChatAttachmentOut],
)
async def upload_chat_attachment(
    session_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:generate"))],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
):
    raw = await file.read()
    row = ChatService(db).upload_attachment(
        ctx,
        session_id,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
        data=raw,
    )
    db.commit()
    db.refresh(row)
    return APIResponse(message="OK", data=_attachment_out(row))


@chat_router.get("/attachments/{attachment_id}/file")
def download_chat_attachment(
    attachment_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    data, content_type, filename = ChatService(db).read_attachment_bytes(ctx, attachment_id)
    headers = {"Content-Disposition": f'inline; filename="{filename}"'}
    return Response(content=data, media_type=content_type, headers=headers)


@chat_router.get(
    "/sessions/{session_id}/messages",
    response_model=APIResponse[list[ChatMessageOut]],
)
def list_chat_messages(
    session_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    svc = ChatService(db)
    rows = svc.list_messages(ctx, session_id)
    atts = svc.list_attachments_for_messages(ctx, [r.id for r in rows])
    return APIResponse(
        message="OK",
        data=[_message_out(r, atts.get(r.id, [])) for r in rows],
    )


@chat_router.post(
    "/sessions/{session_id}/messages",
    response_model=APIResponse[ChatSendResult],
)
def send_chat_message(
    session_id: UUID,
    body: ChatMessageCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:generate"))],
    db: Annotated[Session, Depends(get_db)],
):
    settings = body.settings.model_dump(exclude_none=True) if body.settings else None
    svc = ChatService(db)
    session, user_msg, assistant_msg = svc.send_message(
        ctx,
        session_id,
        content=body.content,
        settings=settings,
        attachment_ids=body.attachment_ids,
        generate_image=body.generate_image,
        image_size=body.image_size,
        image_quality=body.image_quality,
    )
    db.commit()
    db.refresh(session)
    db.refresh(user_msg)
    db.refresh(assistant_msg)
    atts = svc.list_attachments_for_messages(ctx, [user_msg.id, assistant_msg.id])
    return APIResponse(
        message="OK",
        data=ChatSendResult(
            session=_session_out(session),
            user_message=_message_out(user_msg, atts.get(user_msg.id, [])),
            assistant_message=_message_out(assistant_msg, atts.get(assistant_msg.id, [])),
        ),
    )
