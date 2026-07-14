"""Create HrTrainingAttendance table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.hr.models.training_attendance import HrTrainingAttendance  # noqa: F401

revision: str = "0175_hr_training_attendance"
down_revision: str | None = "0174_hr_training"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    HrTrainingAttendance.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    HrTrainingAttendance.__table__.drop(bind=op.get_bind(), checkfirst=True)
