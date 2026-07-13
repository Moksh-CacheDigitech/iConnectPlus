"""Create proc_return_line table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.procurement.models.return_doc import ProcReturnLine  # noqa: F401

revision: str = "0074_proc_return_line"
down_revision: str | None = "0073_proc_return_header"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    ProcReturnLine.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    ProcReturnLine.__table__.drop(bind=op.get_bind(), checkfirst=True)
