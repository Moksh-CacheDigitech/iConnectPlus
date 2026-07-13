"""Create InvBin table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.inventory.models.bin import InvBin  # noqa: F401

revision: str = "0079_inv_bin"
down_revision: str | None = "0078_create_inventory_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    InvBin.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    InvBin.__table__.drop(bind=op.get_bind(), checkfirst=True)
