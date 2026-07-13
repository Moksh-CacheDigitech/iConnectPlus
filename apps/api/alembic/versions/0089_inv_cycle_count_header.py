"""Create InvCycleCountHeader table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.inventory.models.cycle_count import InvCycleCountHeader  # noqa: F401

revision: str = "0089_inv_cycle_count_header"
down_revision: str | None = "0088_inv_adjustment_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    InvCycleCountHeader.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    InvCycleCountHeader.__table__.drop(bind=op.get_bind(), checkfirst=True)
