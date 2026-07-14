"""Create RecCandidateNote table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.models.candidate_note import RecCandidateNote  # noqa: F401

revision: str = "0217_rec_candidate_note"
down_revision: str | None = "0216_rec_talent_pool"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    RecCandidateNote.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    RecCandidateNote.__table__.drop(bind=op.get_bind(), checkfirst=True)
