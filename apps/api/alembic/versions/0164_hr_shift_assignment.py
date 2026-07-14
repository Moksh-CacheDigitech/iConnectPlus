"""Create HrShiftAssignment table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.hr.models.shift_assignment import HrShiftAssignment  # noqa: F401

revision: str = "0164_hr_shift_assignment"
down_revision: str | None = "0163_hr_shift"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    HrShiftAssignment.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    HrShiftAssignment.__table__.drop(bind=op.get_bind(), checkfirst=True)
