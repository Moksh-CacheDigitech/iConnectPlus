"""Create EcReturnItem table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.return_item import EcReturnItem  # noqa: F401

revision: str = "0413_ec_return_item"
down_revision: str | None = "0412_ec_return_request"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcReturnItem.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcReturnItem.__table__.drop(bind=op.get_bind(), checkfirst=True)
