"""System job run claims (tenant-free idempotency for scheduled jobs)."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0634_fnd_job_run"
down_revision: str | Sequence[str] | None = "0633_permission_catalog_sync"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fnd_job_run",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("job_name", sa.String(length=120), nullable=False),
        sa.Column("window_key", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_name", "window_key", name="uk_fnd_job_run_window"),
        schema="foundation",
    )
    op.create_index("ix_fnd_job_run_job_name", "fnd_job_run", ["job_name"], schema="foundation")


def downgrade() -> None:
    op.drop_index("ix_fnd_job_run_job_name", table_name="fnd_job_run", schema="foundation")
    op.drop_table("fnd_job_run", schema="foundation")
