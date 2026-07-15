"""Create IntSyncLog table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.sync_log import IntSyncLog  # noqa: F401

revision: str = "0391_int_sync_log"
down_revision: str | None = "0390_int_sync_job"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntSyncLog.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntSyncLog.__table__.drop(bind=op.get_bind(), checkfirst=True)
