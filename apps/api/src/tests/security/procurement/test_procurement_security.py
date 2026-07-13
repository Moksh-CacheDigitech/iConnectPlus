"""Security tests for procurement RBAC / SoD / tenant isolation hooks."""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.domain.exceptions import SegregationOfDutiesError
from modules.procurement.permissions import (
    BUYER_PERMISSIONS,
    PROC_PERMISSIONS,
    PROCUREMENT_MANAGER_PERMISSIONS,
)
from modules.procurement.service.invoice_service import InvoiceService
from modules.procurement.service.order_service import OrderService
from modules.procurement.service.procurement_scope_validator import ProcurementScopeValidator
from modules.procurement.service.requisition_service import RequisitionService


def _ctx(user_id=None, tenant_id=None) -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id or uuid4(),
        user_id=user_id or uuid4(),
        user_type="employee",
        company_id=uuid4(),
        branch_id=uuid4(),
    )


def test_creator_cannot_approve_requisition() -> None:
    db = MagicMock()
    svc = RequisitionService(db)
    user_id = uuid4()
    ctx = _ctx(user_id=user_id)
    req = MagicMock()
    req.created_by = user_id
    req.workflow_instance_id = uuid4()
    with patch.object(svc, "get_requisition", return_value=req):
        with pytest.raises(SegregationOfDutiesError):
            svc.approve(ctx, uuid4())


def test_creator_cannot_approve_order() -> None:
    db = MagicMock()
    svc = OrderService(db)
    user_id = uuid4()
    ctx = _ctx(user_id=user_id)
    order = MagicMock()
    order.created_by = user_id
    order.workflow_instance_id = uuid4()
    with patch.object(svc, "get_order", return_value=order):
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


def test_scope_rejects_cross_company() -> None:
    from core.exceptions import ForbiddenException

    db = MagicMock()
    validator = ProcurementScopeValidator(db)
    ctx = _ctx()
    with pytest.raises(ForbiddenException):
        validator.validate_company_access(ctx, uuid4())


def test_permissions_cover_p2p_actions() -> None:
    codes = {row[0] for row in PROC_PERMISSIONS}
    for required in (
        "procurement.requisition:convert",
        "procurement.order:approve",
        "procurement.invoice:post",
        "procurement.return:post",
        "procurement.grn:confirm",
    ):
        assert required in codes
    assert "procurement.order:approve" in PROCUREMENT_MANAGER_PERMISSIONS
    assert "procurement.requisition:submit" in BUYER_PERMISSIONS


def test_procurement_tasks_registered() -> None:
    from modules.procurement import tasks

    assert tasks.expire_vendor_quotations.name == "procurement.expire_vendor_quotations"
    assert tasks.retry_invoice_posting.name == "procurement.retry_invoice_posting"
