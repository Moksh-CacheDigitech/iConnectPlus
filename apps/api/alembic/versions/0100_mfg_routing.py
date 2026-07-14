"""Create MfgRouting table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.manufacturing.models.routing import MfgRouting  # noqa: F401

revision: str = "0100_mfg_routing"
down_revision: str | None = "0099_mfg_bom_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    MfgRouting.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    MfgRouting.__table__.drop(bind=op.get_bind(), checkfirst=True)
