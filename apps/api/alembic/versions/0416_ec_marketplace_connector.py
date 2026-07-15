"""Create EcMarketplaceConnector table."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.ecommerce.models.marketplace_connector import EcMarketplaceConnector  # noqa: F401

revision: str = "0416_ec_marketplace_connector"
down_revision: str | None = "0415_ec_promotion"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    EcMarketplaceConnector.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    EcMarketplaceConnector.__table__.drop(bind=op.get_bind(), checkfirst=True)
