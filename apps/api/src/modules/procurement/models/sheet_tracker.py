"""Company-scoped Excel tracker table (extracted grid, merged on re-upload)."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base
from modules.procurement.models.mixins import ProcTransactionMixin


class ProcSheetTracker(Base, *ProcTransactionMixin):
    __tablename__ = "proc_sheet_tracker"
    __table_args__ = {"schema": "procurement"}

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    last_file_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    column_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    row_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    columns_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    rows_json: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    last_merge_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_upload_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
