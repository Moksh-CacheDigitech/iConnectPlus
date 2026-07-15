"""Create SvcServiceFeedback table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.service.models.service_feedback import SvcServiceFeedback  # noqa: F401

revision: str = "0281_svc_service_feedback"
down_revision: str | None = "0280_svc_service_escalation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SvcServiceFeedback.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SvcServiceFeedback.__table__.drop(bind=op.get_bind(), checkfirst=True)
