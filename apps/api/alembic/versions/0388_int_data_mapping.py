"""Create IntDataMapping table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.data_mapping import IntDataMapping  # noqa: F401

revision: str = "0388_int_data_mapping"
down_revision: str | None = "0387_int_retry_and_dlq"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntDataMapping.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntDataMapping.__table__.drop(bind=op.get_bind(), checkfirst=True)
