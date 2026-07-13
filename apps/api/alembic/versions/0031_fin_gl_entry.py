"""Create fin_gl_entry table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.finance.models.ledger import FinGlEntry  # noqa: F401

revision: str = "0031_fin_gl_entry"
down_revision: str | None = "0030_fin_journal_line"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    FinGlEntry.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    FinGlEntry.__table__.drop(bind=op.get_bind(), checkfirst=True)
