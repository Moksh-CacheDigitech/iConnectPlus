"""Unit tests for duplicate checker."""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from core.exceptions import ConflictException
from modules.master_data.models.party import MasterCustomer
from modules.master_data.service.duplicate_checker_service import DuplicateCheckerService


def test_duplicate_code_raises_conflict() -> None:
    db = MagicMock()
    db.scalar.return_value = object()
    checker = DuplicateCheckerService(db)
    with pytest.raises(ConflictException):
        checker.ensure_unique_code(
            model=MasterCustomer,
            company_id=uuid4(),
            code="CUST-00001",
            code_field="customer_code",
            label="Customer",
        )
