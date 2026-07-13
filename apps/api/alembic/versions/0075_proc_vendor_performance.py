"""Create proc_vendor_performance table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.performance import ProcVendorPerformance  # noqa: F401

revision: str = "0075_proc_vendor_performance"
down_revision: str | None = "0074_proc_return_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcVendorPerformance.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcVendorPerformance.__table__.drop(bind=op.get_bind(), checkfirst=True)
