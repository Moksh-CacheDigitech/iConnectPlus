"""Vendor quotation line-item auto-fetch."""

from decimal import Decimal

from modules.crm.domain.vendor_quote_extract import extract_vendor_quote_lines

QUOTE = """
RP TECH INDIA PVT LTD                        Quotation No: RPT/Q/2026/881
Quote Date: 12-09-2026   GSTIN: 27AAACR1234K1Z5
S.No  Description                         HSN     Qty   Unit Price     Amount
1     Dell PowerEdge R760 Server 2x Xeon  84714900  2   5,90,000.00    11,80,000.00
2     Mellanox 100G QSFP28 transceiver    8517    4    31,000        1,24,000
3.    Cat6 patch cord 3m                           40    250.00        10,000.00  18%
Microsoft Windows Server 2022 Standard
16 core licence
4                                                  2    72,000        1,44,000
Sub Total                                                            14,58,000.00
IGST 18%                                                              2,62,440.00
Grand Total                                                          17,20,440.00
Phone: 9876543210 1 2
"""


def test_reconciled_rows_only():
    rows = extract_vendor_quote_lines(QUOTE)
    assert [r["product_name"] for r in rows] == [
        "Dell PowerEdge R760 Server 2x Xeon",
        "Mellanox 100G QSFP28 transceiver",
        "Cat6 patch cord 3m",
        "Microsoft Windows Server 2022 Standard 16 core licence",
    ]
    first = rows[0]
    assert first["hsn_sac"] == "84714900"
    assert first["qty"] == Decimal("2")
    assert first["unit_cost"] == Decimal("590000.00")
    assert first["line_total"] == Decimal("1180000.00")
    assert rows[1]["hsn_sac"] == "8517"
    assert rows[2]["gst_pct"] == Decimal("18")
    assert rows[3]["qty"] == Decimal("2")


def test_totals_and_tax_rows_are_ignored():
    rows = extract_vendor_quote_lines("Total 3 100 300\nCGST 9% 2 50 100\n")
    assert rows == []


def test_empty_text():
    assert extract_vendor_quote_lines("") == []
