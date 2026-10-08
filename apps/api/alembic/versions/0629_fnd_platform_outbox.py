"""Platform outbox, document sequence, and idempotency tables."""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0629_fnd_platform_outbox"
down_revision: str | Sequence[str] | None = "0628_proc_sheet_tracker"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_SCHEMA = "foundation"


def upgrade() -> None:
    op.create_table(
        "fnd_outbox_message",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("aggregate_type", sa.String(length=120), nullable=False),
        sa.Column("aggregate_id", sa.UUID(), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("status", sa.String(length=30), server_default="pending", nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "available_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["foundation.sec_tenant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uk_fnd_outbox_tenant_idempotency"
        ),
        schema=_SCHEMA,
    )
    op.create_index(
        "ix_fnd_outbox_message_tenant_id", "fnd_outbox_message", ["tenant_id"], schema=_SCHEMA
    )
    op.create_index(
        "ix_fnd_outbox_message_event_type", "fnd_outbox_message", ["event_type"], schema=_SCHEMA
    )
    op.create_index(
        "ix_fnd_outbox_message_aggregate_id",
        "fnd_outbox_message",
        ["aggregate_id"],
        schema=_SCHEMA,
    )
    op.create_index(
        "ix_fnd_outbox_message_status", "fnd_outbox_message", ["status"], schema=_SCHEMA
    )

    op.create_table(
        "fnd_document_sequence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=True),
        sa.Column("sequence_key", sa.String(length=120), nullable=False),
        sa.Column("prefix", sa.String(length=40), nullable=False),
        sa.Column("pad_width", sa.Integer(), server_default="6", nullable=False),
        sa.Column("year_bucket", sa.Integer(), server_default="0", nullable=False),
        sa.Column("next_value", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["foundation.sec_tenant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "company_id",
            "sequence_key",
            "year_bucket",
            name="uk_fnd_document_sequence_scope",
        ),
        schema=_SCHEMA,
    )
    op.create_index(
        "ix_fnd_document_sequence_tenant_id",
        "fnd_document_sequence",
        ["tenant_id"],
        schema=_SCHEMA,
    )
    op.create_index(
        "ix_fnd_document_sequence_company_id",
        "fnd_document_sequence",
        ["company_id"],
        schema=_SCHEMA,
    )

    op.create_table(
        "fnd_idempotency_record",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("scope", sa.String(length=80), nullable=False),
        sa.Column("idempotency_key", sa.String(length=200), nullable=False),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["foundation.sec_tenant.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "scope", "idempotency_key", name="uk_fnd_idempotency_scope_key"
        ),
        schema=_SCHEMA,
    )
    op.create_index(
        "ix_fnd_idempotency_record_tenant_id",
        "fnd_idempotency_record",
        ["tenant_id"],
        schema=_SCHEMA,
    )
    op.create_index(
        "ix_fnd_idempotency_record_scope",
        "fnd_idempotency_record",
        ["scope"],
        schema=_SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_fnd_idempotency_record_scope",
        table_name="fnd_idempotency_record",
        schema=_SCHEMA,
    )
    op.drop_index(
        "ix_fnd_idempotency_record_tenant_id",
        table_name="fnd_idempotency_record",
        schema=_SCHEMA,
    )
    op.drop_table("fnd_idempotency_record", schema=_SCHEMA)

    op.drop_index(
        "ix_fnd_document_sequence_company_id",
        table_name="fnd_document_sequence",
        schema=_SCHEMA,
    )
    op.drop_index(
        "ix_fnd_document_sequence_tenant_id",
        table_name="fnd_document_sequence",
        schema=_SCHEMA,
    )
    op.drop_table("fnd_document_sequence", schema=_SCHEMA)

    op.drop_index("ix_fnd_outbox_message_status", table_name="fnd_outbox_message", schema=_SCHEMA)
    op.drop_index(
        "ix_fnd_outbox_message_aggregate_id",
        table_name="fnd_outbox_message",
        schema=_SCHEMA,
    )
    op.drop_index(
        "ix_fnd_outbox_message_event_type",
        table_name="fnd_outbox_message",
        schema=_SCHEMA,
    )
    op.drop_index(
        "ix_fnd_outbox_message_tenant_id",
        table_name="fnd_outbox_message",
        schema=_SCHEMA,
    )
    op.drop_table("fnd_outbox_message", schema=_SCHEMA)
