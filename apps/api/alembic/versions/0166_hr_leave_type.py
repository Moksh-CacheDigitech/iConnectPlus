"""Create HrLeaveType table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.hr.models.leave_type import HrLeaveType  # noqa: F401

revision: str = "0166_hr_leave_type"
down_revision: str | None = "0165_hr_holiday_calendar"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    HrLeaveType.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    HrLeaveType.__table__.drop(bind=op.get_bind(), checkfirst=True)
