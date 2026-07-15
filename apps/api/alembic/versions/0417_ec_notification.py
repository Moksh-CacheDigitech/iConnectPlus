"""Create EcNotification table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.notification import EcNotification  # noqa: F401

revision: str = "0417_ec_notification"
down_revision: str | None = "0416_ec_marketplace_connector"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcNotification.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcNotification.__table__.drop(bind=op.get_bind(), checkfirst=True)
