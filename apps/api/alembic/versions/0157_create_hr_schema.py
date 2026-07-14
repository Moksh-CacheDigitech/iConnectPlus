"""Create hr schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0157_create_hr_schema"
down_revision: str | None = "0156_seed_crm_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS hr")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS hr CASCADE")
