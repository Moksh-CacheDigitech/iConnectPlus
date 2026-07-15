"""Create IntNotification table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.notification import IntNotification  # noqa: F401

revision: str = "0394_int_notification"
down_revision: str | None = "0393_int_rate_limit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntNotification.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntNotification.__table__.drop(bind=op.get_bind(), checkfirst=True)
