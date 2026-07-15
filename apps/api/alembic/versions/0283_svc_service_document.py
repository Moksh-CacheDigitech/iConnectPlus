"""Create SvcServiceDocument table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.service.models.service_document import SvcServiceDocument  # noqa: F401

revision: str = "0283_svc_service_document"
down_revision: str | None = "0282_svc_service_resolution"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SvcServiceDocument.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SvcServiceDocument.__table__.drop(bind=op.get_bind(), checkfirst=True)
