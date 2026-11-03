"""Marketing ChatGPT sessions (one conversation thread per user)."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.marketing.models.mixins import MktTransactionMixin


class MktChatSession(Base, *MktTransactionMixin):
    __tablename__ = "mkt_chat_session"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active','archived')",
            name="ck_mkt_chat_session_status",
        ),
        {"schema": "marketing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New chat")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", index=True)
    settings_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_model: Mapped[str | None] = mapped_column(String(120), nullable=True)


class MktChatMessage(Base, *MktTransactionMixin):
    __tablename__ = "mkt_chat_message"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user','assistant','system')",
            name="ck_mkt_chat_message_role",
        ),
        {"schema": "marketing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("marketing.mkt_chat_session.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    usage_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    meta_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class MktChatAttachment(Base, *MktTransactionMixin):
    """User-uploaded or assistant-generated files attached to a chat message."""

    __tablename__ = "mkt_chat_attachment"
    __table_args__ = (
        CheckConstraint(
            "kind IN ('image','document','generated_image')",
            name="ck_mkt_chat_attachment_kind",
        ),
        CheckConstraint(
            "status IN ('pending','attached','failed')",
            name="ck_mkt_chat_attachment_status",
        ),
        {"schema": "marketing"},
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("marketing.mkt_chat_session.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("marketing.mkt_chat_message.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storage_relpath: Mapped[str] = mapped_column(String(500), nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
