"""Create service time entry and expense tables."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.service.models.service_time_entry import SvcServiceTimeEntry  # noqa: F401
from modules.service.models.service_expense import SvcServiceExpense  # noqa: F401

revision: str = "0278_svc_time_expense"
down_revision: str | None = "0277_svc_service_material"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    SvcServiceTimeEntry.__table__.create(bind=op.get_bind(), checkfirst=True)
    SvcServiceExpense.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    SvcServiceExpense.__table__.drop(bind=op.get_bind(), checkfirst=True)
    SvcServiceTimeEntry.__table__.drop(bind=op.get_bind(), checkfirst=True)
