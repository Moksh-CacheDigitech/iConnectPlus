"""Create MfgMachine table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.manufacturing.models.machine import MfgMachine  # noqa: F401

revision: str = "0097_mfg_machine"
down_revision: str | None = "0096_mfg_work_center"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    MfgMachine.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    MfgMachine.__table__.drop(bind=op.get_bind(), checkfirst=True)
