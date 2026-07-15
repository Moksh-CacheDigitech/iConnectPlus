"""Create int_retry_queue and int_dead_letter tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.integration.models.retry_queue import IntRetryQueue  # noqa: F401
from modules.integration.models.dead_letter import IntDeadLetter  # noqa: F401

revision: str = "0387_int_retry_and_dlq"
down_revision: str | None = "0386_int_message"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    IntRetryQueue.__table__.create(bind=op.get_bind(), checkfirst=True)
    IntDeadLetter.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IntDeadLetter.__table__.drop(bind=op.get_bind(), checkfirst=True)
    IntRetryQueue.__table__.drop(bind=op.get_bind(), checkfirst=True)
