"""Create RecInterviewFeedback table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.models.interview_feedback import RecInterviewFeedback  # noqa: F401

revision: str = "0211_rec_interview_feedback"
down_revision: str | None = "0210_rec_interview"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    RecInterviewFeedback.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    RecInterviewFeedback.__table__.drop(bind=op.get_bind(), checkfirst=True)
