"""Create proc_grn_header table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.grn import ProcGrnHeader  # noqa: F401

revision: str = "0067_proc_grn_header"
down_revision: str | None = "0066_proc_order_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcGrnHeader.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcGrnHeader.__table__.drop(bind=op.get_bind(), checkfirst=True)
