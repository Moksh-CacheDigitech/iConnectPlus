"""Create SvcServiceEscalation table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.service.models.service_escalation import SvcServiceEscalation  # noqa: F401

revision: str = "0280_svc_service_escalation"
down_revision: str | None = "0279_svc_service_sla"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SvcServiceEscalation.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SvcServiceEscalation.__table__.drop(bind=op.get_bind(), checkfirst=True)
