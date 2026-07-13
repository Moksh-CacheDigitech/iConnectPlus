"""Create procurement schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0056_create_procurement_schema"
down_revision: str | None = "0055_seed_sales_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS procurement")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS procurement CASCADE")
