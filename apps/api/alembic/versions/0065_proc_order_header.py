"""Create proc_order_header table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.order import ProcOrderHeader  # noqa: F401

revision: str = "0065_proc_order_header"
down_revision: str | None = "0064_proc_vendor_comparison"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcOrderHeader.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcOrderHeader.__table__.drop(bind=op.get_bind(), checkfirst=True)
