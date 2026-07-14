"""Create RecBackgroundVerification table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.recruitment.models.background_verification import RecBackgroundVerification  # noqa: F401

revision: str = "0214_rec_background_verif"
down_revision: str | None = "0213_rec_offer_approval"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    RecBackgroundVerification.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    RecBackgroundVerification.__table__.drop(bind=op.get_bind(), checkfirst=True)
