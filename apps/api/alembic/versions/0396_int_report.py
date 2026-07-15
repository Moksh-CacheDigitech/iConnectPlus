"""Create IntReport table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.report import IntReport  # noqa: F401

revision: str = "0396_int_report"
down_revision: str | None = "0395_int_monitor"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntReport.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntReport.__table__.drop(bind=op.get_bind(), checkfirst=True)
