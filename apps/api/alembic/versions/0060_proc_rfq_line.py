"""Create proc_rfq_line table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.rfq import ProcRfqLine  # noqa: F401

revision: str = "0060_proc_rfq_line"
down_revision: str | None = "0059_proc_rfq_header"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcRfqLine.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcRfqLine.__table__.drop(bind=op.get_bind(), checkfirst=True)
