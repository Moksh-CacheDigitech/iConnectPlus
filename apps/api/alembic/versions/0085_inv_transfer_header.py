"""Create InvTransferHeader table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.inventory.models.transfer import InvTransferHeader  # noqa: F401

revision: str = "0085_inv_transfer_header"
down_revision: str | None = "0084_inv_reservation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    InvTransferHeader.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    InvTransferHeader.__table__.drop(bind=op.get_bind(), checkfirst=True)
