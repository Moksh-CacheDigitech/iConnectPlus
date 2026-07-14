"""Create RecTalentPool table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.models.talent_pool import RecTalentPool  # noqa: F401

revision: str = "0216_rec_talent_pool"
down_revision: str | None = "0215_rec_reference_check"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    RecTalentPool.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    RecTalentPool.__table__.drop(bind=op.get_bind(), checkfirst=True)
