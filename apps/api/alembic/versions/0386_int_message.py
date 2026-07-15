"""Create IntMessage table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.message import IntMessage  # noqa: F401

revision: str = "0386_int_message"
down_revision: str | None = "0385_int_message_queue"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntMessage.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntMessage.__table__.drop(bind=op.get_bind(), checkfirst=True)
