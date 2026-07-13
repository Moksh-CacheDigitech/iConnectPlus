"""Create InvBatch table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.inventory.models.batch import InvBatch  # noqa: F401

revision: str = "0080_inv_batch"
down_revision: str | None = "0079_inv_bin"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    InvBatch.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    InvBatch.__table__.drop(bind=op.get_bind(), checkfirst=True)
