"""Customer PO header auto-fetch."""

from datetime import date

from modules.crm.domain.customer_po_extract import (
    extract_customer_po_fields,
    find_gstins,
    find_po_date,
    find_po_number,
    parse_date_token,
)

SAMPLE_PO = """
BHARTI AIRTEL LIMITED
PURCHASE ORDER
PO No: 7100045321/UPE          PO Date: 14-08-2026
Bill To: Bharti Airtel Ltd
Plot 16, Udyog Vihar Phase IV
Gurugram, Haryana 122015
GSTIN: 06AAACB2894G1ZK
Ship To: Airtel Warehouse, Gangaganj
Lucknow, Uttar Pradesh 226001
GSTIN: 09AAACB2894G1ZX
Vendor GSTIN: 07AAECC1234F1Z5
Delivery: 16-18 weeks from PO date
"""


def test_po_number_and_date():
    assert find_po_number(SAMPLE_PO) == "7100045321/UPE"
    assert find_po_date(SAMPLE_PO) == date(2026, 8, 14)


def test_date_token_formats():
    assert parse_date_token("14/08/2026") == date(2026, 8, 14)
    assert parse_date_token("14-Aug-2026") == date(2026, 8, 14)
    assert parse_date_token("14 August 2026") == date(2026, 8, 14)
    assert parse_date_token("99/99/9999") is None


def test_gstins_exclude_our_own():
    assert find_gstins(SAMPLE_PO, exclude=["07AAECC1234F1Z5"]) == ["06AAACB2894G1ZK", "09AAACB2894G1ZX"]


def test_full_extract():
    fields = extract_customer_po_fields(SAMPLE_PO, own_gstins=["07AAECC1234F1Z5"])
    assert fields["po_number"] == "7100045321/UPE"
    assert fields["po_date"] == date(2026, 8, 14)
    assert fields["billing_address"].startswith("Bharti Airtel Ltd, Plot 16")
    assert fields["shipping_address"].startswith("Airtel Warehouse, Gangaganj")
    assert [g["state"] for g in fields["gst_registrations"]] == ["Haryana", "Uttar Pradesh"]
    assert (fields["delivery_weeks_min"], fields["delivery_weeks_max"]) == (16, 18)
    assert fields["text_extracted"] is True


def test_empty_document():
    fields = extract_customer_po_fields("")
    assert fields["po_number"] is None
    assert fields["gst_registrations"] == []
    assert fields["text_extracted"] is False
