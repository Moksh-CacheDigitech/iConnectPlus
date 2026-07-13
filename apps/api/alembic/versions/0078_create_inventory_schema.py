"""Create inventory schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0078_create_inventory_schema"
down_revision: str | None = "0077_seed_proc_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS inventory")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS inventory CASCADE")
