"""Create master reference tables: uom, currency, tax."""

import sys
from collections.abc import Sequence
from pathlib import Path

from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.master_data.models.reference import MasterCurrency, MasterTax, MasterUom  # noqa: F401

revision: str = "0014_master_reference_tables"
down_revision: str | None = "0013_create_master_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    MasterUom.__table__.create(bind=bind, checkfirst=True)
    MasterCurrency.__table__.create(bind=bind, checkfirst=True)
    MasterTax.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    MasterTax.__table__.drop(bind=bind, checkfirst=True)
    MasterCurrency.__table__.drop(bind=bind, checkfirst=True)
    MasterUom.__table__.drop(bind=bind, checkfirst=True)
