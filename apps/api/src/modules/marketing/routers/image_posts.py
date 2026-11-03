"""Image post generation + Canva edit handoff."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from modules.marketing.dependencies import (
    PaginationParams,
    TenantContext,
    get_db,
    get_pagination,
    paginate,
    require_permission,
)
from modules.marketing.schemas import GeneratedContentResponse
from modules.marketing.service.image_post_service import ImagePostService
from shared.schemas import APIResponse

image_posts_router = APIRouter(prefix="/image-posts", tags=["Marketing - Image Posts"])


class ImagePostCreativeSpec(BaseModel):
    """Target deliverable from the marketing format catalog (UI)."""

    category_id: str | None = None
    category_label: str | None = None
    format_id: str | None = None
    format_label: str | None = None
    width_px: int | None = None
    height_px: int | None = None
    inches: str | None = None
    cms: str | None = None


class ImagePostCreate(BaseModel):
    prompt: str = Field(min_length=8, max_length=4000)
    size: str = "1024x1024"
    quality: str = "low"
    platform: str | None = None
    creative: ImagePostCreativeSpec | None = None
    company_id: UUID | None = None
    campaign_id: UUID | None = None


class ImagePostRepurpose(BaseModel):
    prompt: str = Field(min_length=8, max_length=4000)
    size: str | None = None
    quality: str | None = None


class ImagePostProvidersResponse(BaseModel):
    openai_configured: bool
    canva_configured: bool
    canva_connected: bool
    canva_scopes: str
    sizes: list[str]
    qualities: list[str] = []
    default_quality: str = "low"


class CanvaAuthorizeResponse(BaseModel):
    authorize_url: str
    state: str


class CanvaExchangeBody(BaseModel):
    code: str
    state: str


class CanvaExchangeResponse(BaseModel):
    connected: bool
    return_to: str
    user_id: str


class EditInCanvaResponse(BaseModel):
    content: GeneratedContentResponse
    canva_edit_url: str
    mode: str | None = None
    canva_design_id: str | None = None
    fallback_reason: str | None = None


class ImageSpendBucket(BaseModel):
    usd: float
    tokens: int
    image_count: int


class ImageSpendLast(BaseModel):
    content_id: str | None = None
    created_at: str | None = None
    usd: float = 0.0
    tokens: int = 0
    text_input_tokens: int = 0
    image_output_tokens: int = 0
    source: str | None = None
    model: str | None = None
    size: str | None = None
    quality: str | None = None


class ImageSpendFx(BaseModel):
    usd_inr: float
    as_of: str | None = None
    source: str = "frankfurter"
    provider: str = "frankfurter"
    provider_url: str | None = None


class ImageSpendSummary(BaseModel):
    currency: str = "USD"
    today: ImageSpendBucket
    last_7_days: ImageSpendBucket
    last_image: ImageSpendLast
    rates: dict[str, float]
    fx: ImageSpendFx | None = None


@image_posts_router.get("/providers", response_model=APIResponse[ImagePostProvidersResponse])
def image_post_providers(
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ImagePostService(db).provider_status(ctx))


@image_posts_router.get("/usage", response_model=APIResponse[ImageSpendSummary])
def image_post_usage(
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
    company_id: UUID | None = None,
    refresh_fx: bool = False,
):
    data = ImagePostService(db).usage_summary(ctx, company_id, refresh_fx=refresh_fx)
    db.commit()
    return APIResponse(message="OK", data=data)


@image_posts_router.get("/canva/authorize", response_model=APIResponse[CanvaAuthorizeResponse])
def canva_authorize(
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:update"))],
    db: Annotated[Session, Depends(get_db)],
    return_to: Annotated[str | None, Query()] = None,
):
    data = ImagePostService(db).canva_authorize_url(ctx, return_to=return_to)
    return APIResponse(message="OK", data=data)


@image_posts_router.post("/canva/exchange", response_model=APIResponse[CanvaExchangeResponse])
def canva_exchange(
    body: CanvaExchangeBody,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    # ctx proves the browser session; state carries the authorizing user_id.
    data = ImagePostService(db).canva_exchange(code=body.code, state=body.state)
    if str(data.get("user_id")) != str(ctx.user_id):
        from modules.marketing.domain.exceptions import ValidationException

        raise ValidationException("Canva OAuth user mismatch. Sign in again and reconnect.")
    return APIResponse(message="OK", data=data)


@image_posts_router.get("", response_model=APIResponse[list[GeneratedContentResponse]])
def list_image_posts(
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    rows = ImagePostService(db).list_posts(ctx, company_id)
    return APIResponse(message="OK", data=paginate(rows, pagination))


@image_posts_router.post("", response_model=APIResponse[GeneratedContentResponse])
def create_image_post(
    body: ImagePostCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:generate"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ImagePostService(db).generate(
        ctx,
        prompt=body.prompt,
        size=body.size,
        quality=body.quality,
        platform=body.platform,
        creative=body.creative.model_dump(exclude_none=True) if body.creative else None,
        company_id=body.company_id,
        campaign_id=body.campaign_id,
    )
    db.commit()
    db.refresh(row)
    return APIResponse(message="OK", data=row)


@image_posts_router.get("/{content_id}", response_model=APIResponse[GeneratedContentResponse])
def get_image_post(
    content_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ImagePostService(db).get_post(ctx, content_id))


@image_posts_router.get("/{content_id}/file")
def get_image_post_file(
    content_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    data, content_type = ImagePostService(db).read_image_bytes(ctx, content_id)
    return Response(content=data, media_type=content_type)


@image_posts_router.post(
    "/{content_id}/repurpose",
    response_model=APIResponse[GeneratedContentResponse],
)
def repurpose_image_post(
    content_id: UUID,
    body: ImagePostRepurpose,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:generate"))],
    db: Annotated[Session, Depends(get_db)],
):
    """Create a new image version from an existing post; source row is kept."""
    row = ImagePostService(db).repurpose(
        ctx,
        content_id,
        prompt=body.prompt,
        size=body.size,
        quality=body.quality,
    )
    db.commit()
    db.refresh(row)
    return APIResponse(message="OK", data=row)


@image_posts_router.post(
    "/{content_id}/edit-in-canva",
    response_model=APIResponse[EditInCanvaResponse],
)
def edit_image_post_in_canva(
    content_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("marketing.content:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ImagePostService(db).edit_in_canva(ctx, content_id)
    db.commit()
    db.refresh(row)
    canva = (row.pipeline_result or {}).get("canva") or {}
    edit_url = canva.get("canva_edit_url")
    if not edit_url:
        from modules.marketing.domain.exceptions import ValidationException

        raise ValidationException("Canva did not return an edit URL")
    return APIResponse(
        message="OK",
        data={
            "content": row,
            "canva_edit_url": edit_url,
            "mode": canva.get("mode"),
            "canva_design_id": canva.get("canva_design_id"),
            "fallback_reason": canva.get("fallback_reason"),
        },
    )
