"""Create HrShift table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.hr.models.shift import HrShift  # noqa: F401

revision: str = "0163_hr_shift"
down_revision: str | None = "0162_hr_designation_assignment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    HrShift.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    HrShift.__table__.drop(bind=op.get_bind(), checkfirst=True)
