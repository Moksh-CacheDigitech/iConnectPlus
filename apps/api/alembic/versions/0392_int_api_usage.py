"""Create IntApiUsage table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.api_usage import IntApiUsage  # noqa: F401

revision: str = "0392_int_api_usage"
down_revision: str | None = "0391_int_sync_log"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntApiUsage.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntApiUsage.__table__.drop(bind=op.get_bind(), checkfirst=True)
