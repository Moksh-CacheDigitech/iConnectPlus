"""Create manufacturing schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0095_create_mfg_schema"
down_revision: str | None = "0094_seed_inv_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS manufacturing")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS manufacturing CASCADE")
