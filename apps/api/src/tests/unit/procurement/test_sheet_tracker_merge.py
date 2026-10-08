from modules.procurement.service.sheet_tracker_grid import merge_tracker_table


def test_merge_adds_new_columns_and_rows() -> None:
    existing_columns = [{"id": "site", "label": "Site"}, {"id": "status", "label": "Status"}]
    existing_rows = [{"site": "A1", "status": "Open"}]
    incoming = {
        "columns": [
            {"id": "c1", "label": "Site"},
            {"id": "c2", "label": "Status"},
            {"id": "c3", "label": "Circle"},
        ],
        "rows": [
            {"c1": "A1", "c2": "Open", "c3": "North"},
            {"c1": "B2", "c2": "New", "c3": "West"},
        ],
    }
    merged = merge_tracker_table(existing_columns, existing_rows, incoming)
    labels = [c["label"] for c in merged["columns"]]
    assert labels == ["Site", "Status", "Circle"]
    assert merged["added_columns"] == ["Circle"]
    assert merged["added_rows"] == 1
    assert merged["updated_rows"] == 1
    by_site = {r["site"]: r for r in merged["rows"]}
    assert by_site["A1"]["circle"] == "North"
    assert by_site["B2"]["status"] == "New"


def test_merge_does_not_overwrite_filled_cells() -> None:
    existing_columns = [{"id": "site", "label": "Site"}, {"id": "status", "label": "Status"}]
    existing_rows = [{"site": "A1", "status": "Open"}]
    incoming = {
        "columns": [{"id": "c1", "label": "Site"}, {"id": "c2", "label": "Status"}],
        "rows": [{"c1": "A1", "c2": "Closed"}],
    }
    merged = merge_tracker_table(existing_columns, existing_rows, incoming)
    assert merged["rows"][0]["status"] == "Open"
    assert merged["updated_rows"] == 0
    assert merged["added_rows"] == 0
