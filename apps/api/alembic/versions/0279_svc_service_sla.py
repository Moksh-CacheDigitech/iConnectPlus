"""Create SvcServiceSla table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.service.models.service_sla import SvcServiceSla  # noqa: F401

revision: str = "0279_svc_service_sla"
down_revision: str | None = "0278_svc_time_expense"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SvcServiceSla.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SvcServiceSla.__table__.drop(bind=op.get_bind(), checkfirst=True)
