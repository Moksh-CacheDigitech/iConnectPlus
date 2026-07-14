"""Create project schema."""

from collections.abc import Sequence

from alembic import op

revision: str = "0223_create_project_schema"
down_revision: str | None = "0222_seed_recruitment_workflows"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS project")


def downgrade() -> None:
    op.execute("DROP SCHEMA IF EXISTS project CASCADE")
