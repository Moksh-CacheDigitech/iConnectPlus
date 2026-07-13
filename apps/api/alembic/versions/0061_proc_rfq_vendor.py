"""Create proc_rfq_vendor table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.rfq import ProcRfqVendor  # noqa: F401

revision: str = "0061_proc_rfq_vendor"
down_revision: str | None = "0060_proc_rfq_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcRfqVendor.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcRfqVendor.__table__.drop(bind=op.get_bind(), checkfirst=True)
