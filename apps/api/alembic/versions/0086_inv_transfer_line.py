"""Create InvTransferLine table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.inventory.models.transfer import InvTransferLine  # noqa: F401

revision: str = "0086_inv_transfer_line"
down_revision: str | None = "0085_inv_transfer_header"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    InvTransferLine.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    InvTransferLine.__table__.drop(bind=op.get_bind(), checkfirst=True)
