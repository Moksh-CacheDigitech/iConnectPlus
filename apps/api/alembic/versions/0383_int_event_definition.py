"""Create IntEventDefinition table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.event_definition import IntEventDefinition  # noqa: F401

revision: str = "0383_int_event_definition"
down_revision: str | None = "0382_int_webhook"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntEventDefinition.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntEventDefinition.__table__.drop(bind=op.get_bind(), checkfirst=True)
