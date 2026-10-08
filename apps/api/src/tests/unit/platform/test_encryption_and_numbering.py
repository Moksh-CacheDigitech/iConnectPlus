"""Platform encryption + numbering helpers."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

from modules.platform.encryption import decrypt_field, encrypt_field, mask_field, should_encrypt_field
from modules.platform.evolution import EXTRACT_STATUS, K8S_READY
from modules.platform.helpers.numbering import next_document_number


def test_encrypt_roundtrip() -> None:
    raw = "super-secret-bank-account"
    enc = encrypt_field(raw)
    assert enc is not None and enc.startswith("enc:v1:")
    assert raw not in enc
    assert decrypt_field(enc) == raw


def test_key_rotation_decrypts_values_from_previous_key() -> None:
    from modules.platform import encryption

    with patch.object(encryption.settings, "field_encryption_keys", "old-key"):
        encryption._cipher.cache_clear()
        old_token = encrypt_field("ABCDE1234F")
    with patch.object(encryption.settings, "field_encryption_keys", "new-key,old-key"):
        encryption._cipher.cache_clear()
        assert decrypt_field(old_token) == "ABCDE1234F"
    encryption._cipher.cache_clear()


def test_encrypted_column_types_roundtrip() -> None:
    from modules.platform.encrypted_types import EncryptedBankJSON, EncryptedText

    col = EncryptedText()
    stored = col.process_bind_param("27AAPFU0939F1ZV", None)
    assert stored.startswith("enc:v1:")
    assert col.process_result_value(stored, None) == "27AAPFU0939F1ZV"
    assert col.process_bind_param(stored, None) == stored

    bank = EncryptedBankJSON()
    stored_json = bank.process_bind_param({"account_number": "00112233", "ifsc": "HDFC0001"}, None)
    assert stored_json["ifsc"] == "HDFC0001"
    assert stored_json["account_number"].startswith("enc:v1:")
    assert bank.process_result_value(stored_json, None)["account_number"] == "00112233"


def test_mask_and_classification() -> None:
    assert should_encrypt_field("api_secret")
    assert mask_field("1234567890", visible_tail=4) == "******7890"


def test_evolution_gates_not_ready_for_extract() -> None:
    assert K8S_READY is False
    assert EXTRACT_STATUS["finance"].ready is False


def test_numbering_helper_delegates() -> None:
    stub = MagicMock()
    stub.next_number.return_value = "TST-000001"
    with patch(
        "modules.platform.helpers.numbering.DocumentNumberingAdapter",
        return_value=stub,
    ):
        code = next_document_number(
            MagicMock(),
            tenant_id=uuid4(),
            company_id=uuid4(),
            sequence_key="test.seq",
            prefix="TST-",
        )
    assert code == "TST-000001"
