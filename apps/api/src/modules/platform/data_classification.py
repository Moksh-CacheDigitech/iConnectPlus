"""Data classification + sensitive-field inventory (security baseline)."""

from __future__ import annotations

from enum import Enum


class DataClass(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


# Fields that must be encrypted at rest / never logged in plaintext.
ENCRYPTED_FIELD_INVENTORY: frozenset[str] = frozenset(
    {
        "password_hash",
        "refresh_token_hash",
        "bank_account_number",
        "tax_id",
        "tax_number",
        "pan",
        "pan_number",
        "aadhaar",
        "api_secret",
        "oauth_client_secret",
        "payment_token",
        "ssn",
        "bank_details_json",
        "secret_vault_ref",
        "client_secret_vault_ref",
    }
)


TABLE_CLASSIFICATION: dict[str, DataClass] = {
    "foundation.sec_user": DataClass.CONFIDENTIAL,
    "foundation.sec_session": DataClass.RESTRICTED,
    "foundation.sec_refresh_token": DataClass.RESTRICTED,
    "payroll.pay_employee_salary": DataClass.RESTRICTED,
    "finance.fin_bank_account": DataClass.RESTRICTED,
    "master_data.master_vendor": DataClass.CONFIDENTIAL,
    "master_data.master_customer": DataClass.CONFIDENTIAL,
    "audit.audit_log": DataClass.CONFIDENTIAL,
}
