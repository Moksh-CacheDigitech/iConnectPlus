"""Security tests for sales RBAC / SoD / tenant isolation hooks."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from modules.foundation.domain.value_objects import TenantContext
from modules.sales.domain.exceptions import SegregationOfDutiesError
from modules.sales.permissions import SALES_MANAGER_PERMISSIONS, SALES_PERMISSIONS
from modules.sales.service.invoice_service import InvoiceService
from modules.sales.service.quotation_service import QuotationService
from modules.sales.service.return_service import ReturnService
from modules.sales.service.sales_scope_validator import SalesScopeValidator


def _ctx(user_id=None, tenant_id=None) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id or uuid4(),
        user_id=user_id or uuid4(),
        user_type="employee",
        company_id=uuid4(),
        branch_id=uuid4(),
    )


def test_creator_cannot_approve_quotation() -> None:
    db = MagicMock()
    svc = QuotationService(db)
    user_id = uuid4()
    ctx = _ctx(user_id=user_id)
    quotation = MagicMock()
    quotation.created_by = user_id
    quotation.workflow_instance_id = uuid4()
    with patch.object(svc, "get_quotation", return_value=quotation):
        with pytest.raises(SegregationOfDutiesError):
            svc.approve(ctx, uuid4())


def test_creator_cannot_approve_invoice() -> None:
    db = MagicMock()
    svc = InvoiceService(db)
    user_id = uuid4()
    ctx = _ctx(user_id=user_id)
    invoice = MagicMock()
    invoice.created_by = user_id
    invoice.workflow_instance_id = uuid4()
    with patch.object(svc, "get_invoice", return_value=invoice):
        with pytest.raises(SegregationOfDutiesError):
            svc.approve(ctx, uuid4())


def test_creator_cannot_approve_return() -> None:
    db = MagicMock()
    svc = ReturnService(db)
    user_id = uuid4()
    ctx = _ctx(user_id=user_id)
    ret = MagicMock()
    ret.created_by = user_id
    ret.workflow_instance_id = uuid4()
    with patch.object(svc, "get_return", return_value=ret):
        with pytest.raises(SegregationOfDutiesError):
            svc.approve(ctx, uuid4())


def test_scope_rejects_cross_company() -> None:
    from core.exceptions import ForbiddenException

    db = MagicMock()
    validator = SalesScopeValidator(db)
    ctx = _ctx()
    with pytest.raises(ForbiddenException):
        validator.validate_company_access(ctx, uuid4())


def test_permissions_cover_o2c_actions() -> None:
    codes = {row[0] for row in SALES_PERMISSIONS}
    for required in (
        "sales.quotation:convert",
        "sales.order:confirm",
        "sales.invoice:post",
        "sales.return:post",
        "sales.order:credit_override",
    ):
        assert required in codes
    assert "sales.invoice:approve" in SALES_MANAGER_PERMISSIONS


def test_sales_tasks_registered() -> None:
    from modules.sales import tasks

    assert tasks.expire_quotations.name == "sales.expire_quotations"
    assert tasks.retry_invoice_posting.name == "sales.retry_invoice_posting"
