"""Marketing Chat sessions + OpenAI completions with durable multimodal history."""

from __future__ import annotations

import base64
import re
import zipfile
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from uuid import UUID, uuid4
from xml.etree import ElementTree

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings
from modules.foundation.domain.value_objects import TenantContext
from modules.marketing.adapters.chat_adapter import ChatAdapter
from modules.marketing.adapters.image_gen_adapter import ImageGenAdapter
from modules.marketing.domain.exceptions import NotFoundException, ValidationException
from modules.marketing.models.brand_voice import MktBrandVoice
from modules.marketing.models.chat_session import (
    MktChatAttachment,
    MktChatMessage,
    MktChatSession,
)
from modules.marketing.repository.base import MktScopedRepository, utcnow
from modules.marketing.service.chat_cost import DEFAULT_CHAT_RATES, cost_from_chat_usage
from modules.platform.compat.audit_facade import PlatformAuditFacade

DEFAULT_SYSTEM = (
    "You are the iConnect Plus marketing assistant. Prefer brand-safe, B2B-ready copy. "
    "Ask clarifying questions when the brief is thin. "
    "When the user shares files, the message may include [Attached document: ...] text blocks "
    "and/or image inputs — treat those as the source of truth. Never claim you cannot access "
    "attachments if their content is present in the message. "
    "When you generate or edit an image, briefly describe what you created."
)

MAX_ATTACHMENTS = 5
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_DOC_BYTES = 15 * 1024 * 1024
MAX_EXTRACT_CHARS = 24000

IMAGE_TYPES = frozenset({"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"})
DOC_TYPES = frozenset(
    {
        "application/pdf",
        "text/plain",
        "text/markdown",
        "text/csv",
        "application/json",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
)

_IMAGE_INTENT = re.compile(
    r"\b("
    r"generate|create|make|draw|design|render|illustrat(?:e|ion)|"
    r"image|picture|photo|logo|banner|poster|thumbnail|creative|visual|"
    r"dall-?e|midjourney"
    r")\b",
    re.I,
)
_EDIT_INTENT = re.compile(
    r"\b(edit|modify|change|update|repurpose|restyle|recolor|remove background|"
    r"upscale|crop|variant|variation)\b",
    re.I,
)


class ChatService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._repo = MktScopedRepository(db)
        self._chat = ChatAdapter()
        self._images = ImageGenAdapter()
        self._audit = PlatformAuditFacade(db)
        ensure_chat_tables(db)

    def provider_status(self) -> dict:
        return {
            "openai_configured": self._chat.configured(),
            "image_generation_configured": self._images.configured(),
            "default_model": (getattr(settings, "openai_model", "") or "gpt-4o-mini").strip(),
            "max_attachments": MAX_ATTACHMENTS,
            "allowed_image_types": sorted(IMAGE_TYPES),
            "allowed_document_types": sorted(DOC_TYPES),
        }

    def usage_summary(
        self,
        ctx: TenantContext,
        company_id: UUID | None = None,
        *,
        refresh_fx: bool = False,
    ) -> dict:
        """Today / last-7-days / last-reply OpenAI chat spend (USD + tokens)."""
        company = self._repo.resolve_list_company_id(ctx, company_id)
        stmt = (
            select(MktChatMessage)
            .join(MktChatSession, MktChatSession.id == MktChatMessage.session_id)
            .where(
                MktChatMessage.is_deleted.is_(False),
                MktChatSession.is_deleted.is_(False),
                MktChatSession.user_id == ctx.user_id,
                MktChatMessage.role == "assistant",
                MktChatMessage.usage_json.is_not(None),
            )
            .order_by(MktChatMessage.created_at.desc())
        )
        if company is not None:
            stmt = stmt.where(MktChatSession.company_id == company)
        stmt = self._repo.apply_mkt_filter(stmt, MktChatSession, ctx, branch_scoped=False)
        rows = list(self.db.scalars(stmt).all())

        now = datetime.now(timezone.utc)
        start_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_7d = now - timedelta(days=7)

        today_usd = 0.0
        today_tokens = 0
        today_count = 0
        week_usd = 0.0
        week_tokens = 0
        week_count = 0
        priced: list[tuple[MktChatMessage, dict]] = []

        for row in rows:
            meta = row.meta_json if isinstance(row.meta_json, dict) else {}
            usage = row.usage_json if isinstance(row.usage_json, dict) else None
            cost = cost_from_chat_usage(
                usage,
                model=row.model or (meta.get("model") if isinstance(meta.get("model"), str) else None),
                size=str(meta.get("size") or "1024x1024"),
                quality=str(meta.get("quality") or "auto"),
            )
            if not cost:
                continue
            priced.append((row, cost))
            usd = float(cost.get("usd") or 0)
            tokens = int(cost.get("total_tokens") or 0)
            created = _as_utc(getattr(row, "created_at", None))
            if created is None:
                continue
            if created >= start_7d:
                week_usd += usd
                week_tokens += tokens
                week_count += 1
            if created >= start_today:
                today_usd += usd
                today_tokens += tokens
                today_count += 1

        last_row, last_cost = priced[0] if priced else (None, None)
        last_created = _as_utc(getattr(last_row, "created_at", None)) if last_row else None
        in_rate, out_rate = DEFAULT_CHAT_RATES

        return {
            "currency": "USD",
            "today": {
                "usd": round(today_usd, 6),
                "tokens": today_tokens,
                "message_count": today_count,
            },
            "last_7_days": {
                "usd": round(week_usd, 6),
                "tokens": week_tokens,
                "message_count": week_count,
            },
            "last_reply": {
                "message_id": str(last_row.id) if last_row else None,
                "session_id": str(last_row.session_id) if last_row else None,
                "created_at": last_created.isoformat() if last_created else None,
                "usd": float(last_cost.get("usd") or 0) if last_cost else 0.0,
                "tokens": int(last_cost.get("total_tokens") or 0) if last_cost else 0,
                "prompt_tokens": int(last_cost.get("prompt_tokens") or last_cost.get("text_input_tokens") or 0)
                if last_cost
                else 0,
                "completion_tokens": int(
                    last_cost.get("completion_tokens") or last_cost.get("image_output_tokens") or 0
                )
                if last_cost
                else 0,
                "source": (last_cost or {}).get("source"),
                "model": (last_cost or {}).get("model") or (getattr(last_row, "model", None) if last_row else None),
                "kind": (last_cost or {}).get("kind"),
            },
            "rates": {
                "input_per_m": in_rate,
                "output_per_m": out_rate,
            },
            "fx": self._usd_inr_fx(force_refresh=refresh_fx),
        }

    def _usd_inr_fx(self, *, force_refresh: bool = False) -> dict:
        from modules.marketing.adapters.frankfurter_fx import get_usd_inr_rate

        return get_usd_inr_rate(force_refresh=force_refresh)

    def list_sessions(self, ctx: TenantContext, company_id: UUID | None = None) -> list[MktChatSession]:
        company = self._repo.resolve_list_company_id(ctx, company_id)
        stmt = (
            select(MktChatSession)
            .where(
                MktChatSession.is_deleted.is_(False),
                MktChatSession.user_id == ctx.user_id,
                MktChatSession.status == "active",
            )
            .order_by(
                MktChatSession.last_message_at.desc().nullslast(),
                MktChatSession.updated_at.desc(),
            )
        )
        if company is not None:
            stmt = stmt.where(MktChatSession.company_id == company)
        stmt = self._repo.apply_mkt_filter(stmt, MktChatSession, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt).all())

    def get_session(self, ctx: TenantContext, session_id: UUID) -> MktChatSession:
        row = self._repo.get_by_id(MktChatSession, ctx, session_id, branch_scoped=False)
        if row is None or row.user_id != ctx.user_id:
            raise NotFoundException("Chat session not found")
        return row

    def create_session(
        self,
        ctx: TenantContext,
        *,
        title: str | None = None,
        settings: dict | None = None,
        company_id: UUID | None = None,
    ) -> MktChatSession:
        company = self._repo.resolve_company_id(ctx, company_id)
        row = self._repo.create_row(
            MktChatSession,
            ctx,
            company_id=company,
            user_id=ctx.user_id,
            title=(title or "New chat").strip()[:255] or "New chat",
            status="active",
            settings_json=settings if isinstance(settings, dict) else None,
            message_count=0,
            last_message_at=None,
            last_model=None,
        )
        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mkt_chat_session",
            entity_id=row.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={"title": row.title},
        )
        return row

    def rename_session(self, ctx: TenantContext, session_id: UUID, title: str) -> MktChatSession:
        row = self.get_session(ctx, session_id)
        clean = (title or "").strip()[:255]
        if not clean:
            raise ValidationException("Title is required")
        row.title = clean
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        self.db.flush()
        return row

    def archive_session(self, ctx: TenantContext, session_id: UUID) -> None:
        row = self.get_session(ctx, session_id)
        row.status = "archived"
        row.is_deleted = True
        row.deleted_at = utcnow()
        row.deleted_by = ctx.user_id
        row.updated_at = utcnow()
        row.updated_by = ctx.user_id
        self.db.flush()

    def list_messages(self, ctx: TenantContext, session_id: UUID) -> list[MktChatMessage]:
        session = self.get_session(ctx, session_id)
        stmt = (
            select(MktChatMessage)
            .where(
                MktChatMessage.is_deleted.is_(False),
                MktChatMessage.session_id == session.id,
            )
            .order_by(MktChatMessage.sequence_no.asc(), MktChatMessage.created_at.asc())
        )
        stmt = self._repo.apply_mkt_filter(stmt, MktChatMessage, ctx, branch_scoped=False)
        return list(self.db.scalars(stmt).all())

    def list_attachments_for_messages(
        self, ctx: TenantContext, message_ids: list[UUID]
    ) -> dict[UUID, list[MktChatAttachment]]:
        if not message_ids:
            return {}
        stmt = select(MktChatAttachment).where(
            MktChatAttachment.is_deleted.is_(False),
            MktChatAttachment.message_id.in_(message_ids),
            MktChatAttachment.status == "attached",
        )
        stmt = self._repo.apply_mkt_filter(stmt, MktChatAttachment, ctx, branch_scoped=False)
        out: dict[UUID, list[MktChatAttachment]] = {}
        for row in self.db.scalars(stmt).all():
            if row.message_id is None:
                continue
            out.setdefault(row.message_id, []).append(row)
        for rows in out.values():
            rows.sort(key=lambda r: r.created_at or utcnow())
        return out

    def start_from_image_post(
        self,
        ctx: TenantContext,
        content_id: UUID,
        *,
        settings: dict | None = None,
    ) -> tuple[MktChatSession, MktChatAttachment]:
        """Open a Content Studio image post in a new Chat session (pending attachment)."""
        from modules.marketing.service.image_post_service import ImagePostService

        image_svc = ImagePostService(self.db)
        post = image_svc.get_post(ctx, content_id)
        raw, content_type = image_svc.read_image_bytes(ctx, content_id)
        pipeline = post.pipeline_result if isinstance(post.pipeline_result, dict) else {}
        creative = pipeline.get("creative") if isinstance(pipeline.get("creative"), dict) else {}
        format_label = str(creative.get("format_label") or pipeline.get("label") or "Image post")
        title = _title_from_prompt(str(post.headline or format_label or "Image in chat"))
        session = self.create_session(
            ctx,
            title=title,
            settings=settings,
            company_id=post.company_id,
        )
        ext = ".png"
        ctype = (content_type or "image/png").split(";")[0].strip().lower() or "image/png"
        if "jpeg" in ctype or "jpg" in ctype:
            ext = ".jpg"
        elif "webp" in ctype:
            ext = ".webp"
        elif "gif" in ctype:
            ext = ".gif"
        filename = f"{format_label.replace(' ', '_')[:40]}{ext}"
        attachment = self.upload_attachment(
            ctx,
            session.id,
            filename=filename,
            content_type=ctype,
            data=raw,
        )
        attachment.meta_json = {
            **(attachment.meta_json if isinstance(attachment.meta_json, dict) else {}),
            "source": "image_post",
            "content_id": str(post.id),
            "format_label": format_label,
            "platform": pipeline.get("platform"),
            "prompt": pipeline.get("prompt") or post.body,
        }
        self.db.flush()
        return session, attachment

    def upload_attachment(
        self,
        ctx: TenantContext,
        session_id: UUID,
        *,
        filename: str,
        content_type: str,
        data: bytes,
    ) -> MktChatAttachment:
        session = self.get_session(ctx, session_id)
        clean_name = Path(filename or "upload.bin").name[:255] or "upload.bin"
        ctype = (content_type or "application/octet-stream").split(";")[0].strip().lower()
        if ctype == "image/jpg":
            ctype = "image/jpeg"

        if ctype in IMAGE_TYPES:
            kind = "image"
            if len(data) > MAX_IMAGE_BYTES:
                raise ValidationException("Image exceeds 10 MB limit")
        elif ctype in DOC_TYPES or _looks_like_text(clean_name, ctype):
            kind = "document"
            if len(data) > MAX_DOC_BYTES:
                raise ValidationException("Document exceeds 15 MB limit")
        else:
            raise ValidationException(
                f"Unsupported file type {ctype or 'unknown'}. Upload images (PNG/JPEG/WebP/GIF) "
                "or documents (PDF, TXT, MD, CSV, JSON, DOCX, XLSX)."
            )
        if len(data) < 1:
            raise ValidationException("File is empty")

        pending = self._count_pending(ctx, session.id)
        if pending >= MAX_ATTACHMENTS:
            raise ValidationException(f"At most {MAX_ATTACHMENTS} pending attachments per message")

        rel = f"{session.tenant_id}/{session.id}/{uuid4().hex}_{clean_name}"
        path = _chat_root() / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

        extracted = None
        if kind == "document":
            extracted = _extract_document_text(data, ctype, clean_name)

        row = self._repo.create_row(
            MktChatAttachment,
            ctx,
            company_id=session.company_id,
            session_id=session.id,
            message_id=None,
            kind=kind,
            status="pending",
            filename=clean_name,
            content_type=ctype,
            size_bytes=len(data),
            storage_relpath=rel.replace("\\", "/"),
            extracted_text=extracted,
            meta_json={"source": "user_upload"},
        )
        return row

    def get_attachment(self, ctx: TenantContext, attachment_id: UUID) -> MktChatAttachment:
        row = self._repo.get_by_id(MktChatAttachment, ctx, attachment_id, branch_scoped=False)
        if row is None:
            raise NotFoundException("Attachment not found")
        session = self.get_session(ctx, row.session_id)
        if session.id != row.session_id:
            raise NotFoundException("Attachment not found")
        return row

    def read_attachment_bytes(self, ctx: TenantContext, attachment_id: UUID) -> tuple[bytes, str, str]:
        row = self.get_attachment(ctx, attachment_id)
        path = _resolve_attachment_path(row.storage_relpath)
        if path is None:
            raise NotFoundException("Attachment file missing on disk")
        return path.read_bytes(), row.content_type, row.filename

    def send_message(
        self,
        ctx: TenantContext,
        session_id: UUID,
        *,
        content: str,
        settings: dict | None = None,
        attachment_ids: list[UUID] | None = None,
        generate_image: bool | None = None,
        image_size: str | None = None,
        image_quality: str | None = None,
    ) -> tuple[MktChatSession, MktChatMessage, MktChatMessage]:
        text = (content or "").strip()
        if len(text) > 16000:
            raise ValidationException("Message is too long (max 16000 characters)")

        session = self.get_session(ctx, session_id)
        cfg = _merge_settings(session.settings_json, settings)
        if isinstance(settings, dict):
            session.settings_json = cfg

        attachments = self._claim_attachments(ctx, session, attachment_ids or [])
        if not text and not attachments:
            raise ValidationException("Message cannot be empty — add text or attach a file")

        history = self.list_messages(ctx, session.id)
        next_seq = (history[-1].sequence_no + 1) if history else 1

        user_msg = self._repo.create_row(
            MktChatMessage,
            ctx,
            company_id=session.company_id,
            session_id=session.id,
            role="user",
            content=text or _default_user_caption(attachments),
            sequence_no=next_seq,
            usage_json=None,
            meta_json={
                "attachment_count": len(attachments),
                "attachment_kinds": [a.kind for a in attachments],
            },
        )
        for att in attachments:
            att.message_id = user_msg.id
            att.status = "attached"
            att.updated_at = utcnow()
            att.updated_by = ctx.user_id
        self.db.flush()

        want_image = bool(generate_image) or _wants_image_output(text, attachments)
        edit_source = _first_user_image(attachments)
        generated_att: MktChatAttachment | None = None
        assistant_text = ""
        result_model = None
        usage = None
        finish_reason = None
        mode = "chat"

        if want_image and self._images.configured():
            use_edit = bool(
                edit_source
                and (
                    bool(generate_image)
                    or bool(_EDIT_INTENT.search(text or ""))
                )
            )
            if use_edit and edit_source is not None:
                mode = "image_edit"
                raw, ctype, _name = self.read_attachment_bytes(ctx, edit_source.id)
                prompt = text or "Edit this marketing creative while keeping brand-safe layout."
                generated = self._images.edit(
                    image_bytes=raw,
                    prompt=prompt,
                    size=image_size or "1024x1024",
                    quality=image_quality or "low",
                    content_type=ctype,
                )
            else:
                mode = "image_generate"
                prompt = text or "Create a polished marketing visual."
                if attachments:
                    prompt = self._prompt_with_doc_context(prompt, attachments)
                generated = self._images.generate(
                    prompt=prompt,
                    size=image_size or "1024x1024",
                    quality=image_quality or "low",
                )
            generated_att = self._store_generated_image(
                ctx,
                session,
                generated["bytes"],
                content_type=str(generated.get("content_type") or "image/png"),
                meta={
                    "source": mode,
                    "size": generated.get("size"),
                    "quality": generated.get("quality"),
                    "revised_prompt": generated.get("revised_prompt"),
                    "usage": generated.get("usage"),
                },
            )
            result_model = str(generated.get("model") or "") or None
            usage = generated.get("usage") if isinstance(generated.get("usage"), dict) else None
            assistant_text = (
                generated.get("revised_prompt")
                or f"Here’s the {'edited' if mode == 'image_edit' else 'generated'} image."
            )
            # Also get a short caption from chat when possible.
            try:
                caption_messages = self._build_openai_messages(
                    ctx,
                    session,
                    history,
                    text or "Describe the image you just created in 2 short sentences.",
                    cfg,
                    attachments,
                    force_text_only=True,
                )
                caption_messages.append(
                    {
                        "role": "system",
                        "content": "Reply with a brief caption only (2 sentences max). Do not refuse.",
                    }
                )
                caption = self._chat.complete(
                    messages=caption_messages,
                    model=str(cfg.get("model") or "") or None,
                    temperature=0.4,
                    max_tokens=120,
                )
                if caption.get("content"):
                    assistant_text = str(caption["content"]).strip()
            except Exception:
                pass
        else:
            openai_messages = self._build_openai_messages(
                ctx, session, history, text, cfg, attachments
            )
            result = self._chat.complete(
                messages=openai_messages,
                model=str(cfg.get("model") or "") or None,
                temperature=float(cfg.get("temperature") or 0.7),
                max_tokens=int(cfg.get("maxTokens") or cfg.get("max_tokens") or 2048),
            )
            assistant_text = result["content"]
            result_model = str(result.get("model") or "") or None
            usage = result.get("usage") if isinstance(result.get("usage"), dict) else None
            finish_reason = result.get("finish_reason")

        assistant_msg = self._repo.create_row(
            MktChatMessage,
            ctx,
            company_id=session.company_id,
            session_id=session.id,
            role="assistant",
            content=assistant_text,
            sequence_no=next_seq + 1,
            usage_json=usage,
            meta_json={
                "finish_reason": finish_reason,
                "mode": mode,
                "rag_enabled": bool(cfg.get("ragEnabled")),
                "brand_kit_enabled": bool(cfg.get("brandKitEnabled")),
                "generated_image": bool(generated_att),
            },
        )
        assistant_msg.model = result_model
        if generated_att is not None:
            generated_att.message_id = assistant_msg.id
            generated_att.status = "attached"
            generated_att.updated_at = utcnow()
            generated_att.updated_by = ctx.user_id
        self.db.flush()

        session.message_count = int(session.message_count or 0) + 2
        session.last_message_at = utcnow()
        session.last_model = result_model
        session.updated_at = utcnow()
        session.updated_by = ctx.user_id
        if session.title in ("", "New chat") and next_seq == 1:
            session.title = _title_from_prompt(text or (attachments[0].filename if attachments else "New chat"))
        self.db.flush()

        self._audit.log_entity_change(
            tenant_id=ctx.tenant_id,
            entity_name="mkt_chat_message",
            entity_id=assistant_msg.id,
            operation="create",
            performed_by=ctx.user_id,
            new_value={
                "session_id": str(session.id),
                "model": result_model,
                "mode": mode,
                "tokens": (usage or {}).get("total_tokens") if usage else None,
            },
        )
        return session, user_msg, assistant_msg

    def _claim_attachments(
        self, ctx: TenantContext, session: MktChatSession, attachment_ids: list[UUID]
    ) -> list[MktChatAttachment]:
        if not attachment_ids:
            return []
        if len(attachment_ids) > MAX_ATTACHMENTS:
            raise ValidationException(f"At most {MAX_ATTACHMENTS} attachments per message")
        rows: list[MktChatAttachment] = []
        for aid in attachment_ids:
            row = self.get_attachment(ctx, aid)
            if row.session_id != session.id:
                raise ValidationException("Attachment does not belong to this chat")
            if row.status != "pending" or row.message_id is not None:
                raise ValidationException(f"Attachment {row.filename} is already used")
            rows.append(row)
        return rows

    def _count_pending(self, ctx: TenantContext, session_id: UUID) -> int:
        stmt = select(MktChatAttachment).where(
            MktChatAttachment.is_deleted.is_(False),
            MktChatAttachment.session_id == session_id,
            MktChatAttachment.status == "pending",
            MktChatAttachment.message_id.is_(None),
        )
        stmt = self._repo.apply_mkt_filter(stmt, MktChatAttachment, ctx, branch_scoped=False)
        return len(list(self.db.scalars(stmt).all()))

    def _store_generated_image(
        self,
        ctx: TenantContext,
        session: MktChatSession,
        data: bytes,
        *,
        content_type: str,
        meta: dict,
    ) -> MktChatAttachment:
        ext = ".png"
        if "jpeg" in content_type or "jpg" in content_type:
            ext = ".jpg"
        elif "webp" in content_type:
            ext = ".webp"
        filename = f"generated_{uuid4().hex[:10]}{ext}"
        rel = f"{session.tenant_id}/{session.id}/{uuid4().hex}_{filename}"
        path = _chat_root() / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return self._repo.create_row(
            MktChatAttachment,
            ctx,
            company_id=session.company_id,
            session_id=session.id,
            message_id=None,
            kind="generated_image",
            status="pending",
            filename=filename,
            content_type=content_type or "image/png",
            size_bytes=len(data),
            storage_relpath=rel.replace("\\", "/"),
            extracted_text=None,
            meta_json=meta,
        )

    def _prompt_with_doc_context(self, prompt: str, attachments: list[MktChatAttachment]) -> str:
        parts = [prompt]
        for att in attachments:
            if att.kind == "document" and att.extracted_text:
                parts.append(
                    f"\n\n--- Document: {att.filename} ---\n{att.extracted_text[:8000]}"
                )
        return "\n".join(parts).strip()

    def _build_openai_messages(
        self,
        ctx: TenantContext,
        session: MktChatSession,
        history: list[MktChatMessage],
        user_text: str,
        cfg: dict,
        attachments: list[MktChatAttachment] | None = None,
        *,
        force_text_only: bool = False,
    ) -> list[dict]:
        system = str(cfg.get("systemPrompt") or DEFAULT_SYSTEM).strip() or DEFAULT_SYSTEM
        extras: list[str] = []

        if cfg.get("brandKitEnabled"):
            brand = self._brand_context(ctx, session.company_id, cfg)
            if brand:
                extras.append(brand)

        if cfg.get("ragEnabled"):
            source = str(cfg.get("ragSource") or "documents")
            hint = str(cfg.get("ragIndexHint") or "").strip()
            extras.append(
                "RAG is enabled for this chat. Prefer grounded answers from retrieved marketing "
                f"knowledge (source={source}"
                + (f", index={hint}" if hint else "")
                + "). If retrieval is unavailable, say what you need rather than inventing facts."
            )

        if extras:
            system = system + "\n\n" + "\n\n".join(extras)

        messages: list[dict] = [{"role": "system", "content": system}]
        recent = history[-40:]
        hist_ids = [m.id for m in recent]
        hist_atts = self.list_attachments_for_messages(ctx, hist_ids)

        for row in recent:
            if row.role not in {"user", "assistant", "system"}:
                continue
            atts = hist_atts.get(row.id, [])
            content = self._message_content_parts(row.content, atts, allow_images=not force_text_only)
            if content:
                messages.append({"role": row.role, "content": content})

        current_parts = self._message_content_parts(
            user_text,
            attachments or [],
            allow_images=not force_text_only,
        )
        if current_parts:
            messages.append({"role": "user", "content": current_parts})
        return messages

    def _message_content_parts(
        self,
        text: str,
        attachments: list[MktChatAttachment],
        *,
        allow_images: bool,
    ) -> str | list[dict]:
        clean = (text or "").strip()
        doc_bits: list[str] = []
        image_parts: list[dict] = []

        for att in attachments:
            if att.kind == "document" and att.extracted_text:
                doc_bits.append(
                    f"[Attached document: {att.filename}]\n{att.extracted_text[:MAX_EXTRACT_CHARS]}"
                )
            elif att.kind in {"image", "generated_image"} and allow_images:
                data_url = self._attachment_data_url(att)
                if data_url:
                    image_parts.append(
                        {"type": "image_url", "image_url": {"url": data_url, "detail": "auto"}}
                    )
                else:
                    doc_bits.append(f"[Attached image unavailable: {att.filename}]")

        text_body = clean
        if doc_bits:
            text_body = (clean + "\n\n" if clean else "") + "\n\n".join(doc_bits)

        if not image_parts:
            return text_body or clean or " "
        parts: list[dict] = []
        if text_body:
            parts.append({"type": "text", "text": text_body})
        parts.extend(image_parts)
        return parts

    def _attachment_data_url(self, att: MktChatAttachment) -> str | None:
        path = _resolve_attachment_path(att.storage_relpath)
        if path is None:
            return None
        raw = path.read_bytes()
        # Cap vision payload ~4MB encoded.
        if len(raw) > 3_500_000:
            return None
        b64 = base64.b64encode(raw).decode("ascii")
        ctype = att.content_type or "image/png"
        return f"data:{ctype};base64,{b64}"

    def _brand_context(self, ctx: TenantContext, company_id: UUID, cfg: dict) -> str | None:
        voice_id = str(cfg.get("brandKitVoiceId") or "").strip()
        stmt = select(MktBrandVoice).where(
            MktBrandVoice.is_deleted.is_(False),
            MktBrandVoice.company_id == company_id,
            MktBrandVoice.status.in_(("active", "training", "draft")),
        )
        stmt = self._repo.apply_mkt_filter(stmt, MktBrandVoice, ctx, branch_scoped=False)
        if voice_id:
            try:
                stmt = stmt.where(MktBrandVoice.id == UUID(voice_id))
            except ValueError:
                pass
        else:
            stmt = stmt.order_by(MktBrandVoice.updated_at.desc())
        voice = self.db.scalars(stmt.limit(1)).first()
        if voice is None:
            return None

        parts = [f"Brand voice: {voice.voice_name} ({voice.voice_code})."]
        if cfg.get("brandKitIncludeVoice", True):
            if voice.guidelines:
                parts.append(f"Guidelines: {voice.guidelines[:2000]}")
            keywords = voice.tone_keywords
            if isinstance(keywords, dict):
                tags = keywords.get("tags") or keywords.get("keywords") or list(keywords.values())
            elif isinstance(keywords, list):
                tags = keywords
            else:
                tags = []
            if tags:
                parts.append("Tone keywords: " + ", ".join(str(t) for t in tags[:20]))
        kit = voice.brand_kit if isinstance(voice.brand_kit, dict) else {}
        if cfg.get("brandKitIncludeColors", True) and kit:
            colors = kit.get("colors") or kit.get("palette")
            if colors:
                parts.append(f"Color palette: {colors}")
        if cfg.get("brandKitIncludeLogoRules", True) and kit:
            logo = kit.get("logo") or kit.get("logo_rules")
            if logo:
                parts.append(f"Logo rules: {logo}")
        return "\n".join(parts)


def _merge_settings(existing: dict | None, incoming: dict | None) -> dict:
    base = dict(existing) if isinstance(existing, dict) else {}
    if isinstance(incoming, dict):
        base.update({k: v for k, v in incoming.items() if v is not None})
    return base


def _title_from_prompt(prompt: str) -> str:
    clean = " ".join(prompt.split()).strip()
    if not clean:
        return "New chat"
    return (clean[:42] + "…") if len(clean) > 42 else clean


def _default_user_caption(attachments: list[MktChatAttachment]) -> str:
    if not attachments:
        return "(attachment)"
    names = ", ".join(a.filename for a in attachments[:3])
    return f"Shared: {names}"


def _first_user_image(attachments: list[MktChatAttachment]) -> MktChatAttachment | None:
    for att in attachments:
        if att.kind == "image":
            return att
    return None


def _wants_image_output(text: str, attachments: list[MktChatAttachment]) -> bool:
    clean = (text or "").strip()
    if not clean:
        # Image-only upload → analyze via vision, don't auto-generate.
        return False
    if not _IMAGE_INTENT.search(clean):
        return False
    # "describe this image" should not generate.
    if re.search(r"\b(describe|explain|analyze|analyse|caption|what('?s| is)|read|ocr)\b", clean, re.I):
        if any(a.kind == "image" for a in attachments):
            return False
    return True


def _looks_like_text(filename: str, content_type: str) -> bool:
    if content_type.startswith("text/"):
        return True
    lower = filename.lower()
    return lower.endswith((".txt", ".md", ".csv", ".json", ".log"))


def _chat_root() -> Path:
    base = Path(settings.resolved_crm_upload_root) / "marketing-chat"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _resolve_attachment_path(relpath: str) -> Path | None:
    if not relpath or ".." in relpath:
        return None
    path = _chat_root() / relpath
    try:
        if path.is_file():
            return path
    except OSError:
        return None
    return None


def _extract_document_text(data: bytes, content_type: str, filename: str) -> str | None:
    lower = filename.lower()
    try:
        if content_type == "application/pdf" or lower.endswith(".pdf"):
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(data))
            chunks: list[str] = []
            for page in reader.pages[:40]:
                chunks.append(page.extract_text() or "")
            text = "\n".join(chunks).strip()
            return text[:MAX_EXTRACT_CHARS] or None
        if (
            content_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            or lower.endswith(".docx")
        ):
            return _extract_docx(data)
        if (
            content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            or lower.endswith(".xlsx")
        ):
            return _extract_xlsx(data)
        if content_type.startswith("text/") or lower.endswith(
            (".txt", ".md", ".csv", ".json", ".log")
        ):
            return data.decode("utf-8", errors="replace")[:MAX_EXTRACT_CHARS]
    except Exception:
        return None
    return None


def _extract_docx(data: bytes) -> str | None:
    try:
        with zipfile.ZipFile(BytesIO(data)) as zf:
            xml = zf.read("word/document.xml")
        root = ElementTree.fromstring(xml)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = [node.text for node in root.findall(".//w:t", ns) if node.text]
        joined = "\n".join(texts).strip()
        return joined[:MAX_EXTRACT_CHARS] or None
    except Exception:
        return None


def _extract_xlsx(data: bytes) -> str | None:
    try:
        from openpyxl import load_workbook

        wb = load_workbook(BytesIO(data), read_only=True, data_only=True)
        lines: list[str] = []
        for sheet in wb.worksheets[:5]:
            lines.append(f"# Sheet: {sheet.title}")
            for i, row in enumerate(sheet.iter_rows(values_only=True)):
                if i > 200:
                    break
                cells = ["" if c is None else str(c) for c in row]
                if any(cells):
                    lines.append("\t".join(cells))
        return "\n".join(lines)[:MAX_EXTRACT_CHARS] or None
    except Exception:
        return None


_tables_ready = False


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def ensure_chat_tables(db: Session) -> None:
    """Create chat tables if missing (local DBs may be mid-migration)."""
    global _tables_ready
    if _tables_ready:
        return
    from sqlalchemy import inspect, text

    from database.base import Base
    from modules.foundation.models.security import SecTenant  # noqa: F401
    from modules.organization.models.company import OrgCompany  # noqa: F401

    bind = db.get_bind()
    insp = inspect(bind)
    need_session = not insp.has_table("mkt_chat_session", schema="marketing")
    need_message = not insp.has_table("mkt_chat_message", schema="marketing")
    need_attachment = not insp.has_table("mkt_chat_attachment", schema="marketing")
    if need_session or need_message or need_attachment:
        with bind.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS marketing"))
        tables = []
        if need_session:
            tables.append(MktChatSession.__table__)
        if need_message:
            tables.append(MktChatMessage.__table__)
        if need_attachment:
            tables.append(MktChatAttachment.__table__)
        Base.metadata.create_all(bind=bind, tables=tables, checkfirst=True)
    _tables_ready = True
