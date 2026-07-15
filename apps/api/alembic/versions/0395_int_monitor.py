"""Create IntMonitor table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.monitor import IntMonitor  # noqa: F401

revision: str = "0395_int_monitor"
down_revision: str | None = "0394_int_notification"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntMonitor.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntMonitor.__table__.drop(bind=op.get_bind(), checkfirst=True)
