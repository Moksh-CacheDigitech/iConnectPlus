"""Field-level encryption at rest for tax / KYC / bank / integration secrets.

Widens the columns to TEXT (ciphertext is ~110+ chars), drops btree indexes that
are meaningless on non-deterministic ciphertext, and encrypts existing plaintext
in place using the application key (SECRET_KEY / JWT secret).
"""

import json
import sys
from collections.abc import Sequence
from pathlib import Path

import sqlalchemy as sa
from alembic import op

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from modules.platform.encryption import decrypt_field, encrypt_field

revision: str = "0635_encrypt_sensitive_columns"
down_revision: str | Sequence[str] | None = "0634_fnd_job_run"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TEXT_COLUMNS: tuple[tuple[str, str, str, int], ...] = (
    ("master", "master_customer", "tax_number", 100),
    ("master", "master_vendor", "tax_number", 100),
    ("master", "master_party_registration", "tax_number", 100),
    ("master", "master_party_registration", "pan_number", 20),
    ("hr", "hr_employee_profile", "aadhaar_number", 12),
    ("hr", "hr_employee_profile", "pan_number", 10),
    ("hr", "hr_employee_profile", "bank_account_number", 30),
    ("integration", "int_api_credential", "secret_vault_ref", 255),
    ("integration", "int_oauth_client", "client_secret_vault_ref", 255),
    ("integration", "int_webhook", "secret_vault_ref", 255),
)
BANK_JSON_KEYS = ("account_number", "bank_account_number", "iban", "account_no")


def upgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP INDEX IF EXISTS hr.ix_hr_profile_aadhaar")
    op.execute("DROP INDEX IF EXISTS hr.ix_hr_profile_pan")
    for schema, table, column, _ in TEXT_COLUMNS:
        op.alter_column(table, column, type_=sa.Text(), schema=schema)
        rows = bind.execute(
            sa.text(
                f"SELECT id, {column} FROM {schema}.{table} "
                f"WHERE {column} IS NOT NULL AND {column} <> '' AND {column} NOT LIKE 'enc:%'"
            )
        ).fetchall()
        for row_id, value in rows:
            bind.execute(
                sa.text(f"UPDATE {schema}.{table} SET {column} = :v WHERE id = :id"),
                {"v": encrypt_field(value), "id": row_id},
            )

    rows = bind.execute(
        sa.text(
            "SELECT id, bank_details_json FROM master.master_party_registration "
            "WHERE bank_details_json IS NOT NULL"
        )
    ).fetchall()
    for row_id, payload in rows:
        if not isinstance(payload, dict):
            continue
        changed = dict(payload)
        for key in BANK_JSON_KEYS:
            value = changed.get(key)
            if isinstance(value, str) and value and not value.startswith("enc:"):
                changed[key] = encrypt_field(value)
        if changed != payload:
            bind.execute(
                sa.text(
                    "UPDATE master.master_party_registration "
                    "SET bank_details_json = CAST(:v AS JSONB) WHERE id = :id"
                ),
                {"v": json.dumps(changed), "id": row_id},
            )


def downgrade() -> None:
    bind = op.get_bind()
    for schema, table, column, length in TEXT_COLUMNS:
        rows = bind.execute(
            sa.text(f"SELECT id, {column} FROM {schema}.{table} WHERE {column} LIKE 'enc:%'")
        ).fetchall()
        for row_id, value in rows:
            bind.execute(
                sa.text(f"UPDATE {schema}.{table} SET {column} = :v WHERE id = :id"),
                {"v": decrypt_field(value), "id": row_id},
            )
        op.alter_column(table, column, type_=sa.String(length), schema=schema)
    op.execute("CREATE INDEX IF NOT EXISTS ix_hr_profile_aadhaar ON hr.hr_employee_profile (aadhaar_number)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_hr_profile_pan ON hr.hr_employee_profile (pan_number)")
