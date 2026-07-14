"""Create HrLeaveBalance table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.hr.models.leave_balance import HrLeaveBalance  # noqa: F401

revision: str = "0167_hr_leave_balance"
down_revision: str | None = "0166_hr_leave_type"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    HrLeaveBalance.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    HrLeaveBalance.__table__.drop(bind=op.get_bind(), checkfirst=True)
