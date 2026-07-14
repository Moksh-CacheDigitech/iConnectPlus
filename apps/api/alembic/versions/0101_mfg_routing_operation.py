"""Create MfgRoutingOperation table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.manufacturing.models.routing import MfgRoutingOperation  # noqa: F401

revision: str = "0101_mfg_routing_operation"
down_revision: str | None = "0100_mfg_routing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    MfgRoutingOperation.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    MfgRoutingOperation.__table__.drop(bind=op.get_bind(), checkfirst=True)
