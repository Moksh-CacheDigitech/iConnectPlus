"""Inventory aging buckets."""

import pytest

from modules.procurement.service.inventory_ownership_service import aging_bucket


@pytest.mark.parametrize(
    ("age", "bucket"),
    [(0, "0-30"), (30, "0-30"), (31, "31-90"), (180, "91-180"), (365, "181-365"), (507, "365+")],
)
def test_aging_bucket(age, bucket):
    assert aging_bucket(age) == bucket
