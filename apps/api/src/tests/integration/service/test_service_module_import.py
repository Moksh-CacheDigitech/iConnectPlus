"""Integration smoke: Service module imports and router mount."""

from modules.service.models import SvcServiceCategory, SvcServiceExpense, SvcServiceRequest
from modules.service.router import service_router
from modules.service.service import (
    ServiceApplicationService,
    ServiceExpenseService,
    ServiceRequestService,
    WorkOrderService,
)
from modules.service.service.engines import ServiceExpenseEngine, ServiceRequestEngine


def test_service_models_importable():
    assert SvcServiceCategory.__tablename__ == "svc_service_category"
    assert SvcServiceRequest.__tablename__ == "svc_service_request"
    assert SvcServiceExpense.__tablename__ == "svc_service_expense"


def test_service_router_mounted():
    assert service_router.prefix == "/service"
    paths = [getattr(r, "path", "") for r in service_router.routes]
    assert any("/{row_id}" in p for p in paths)
    assert any("service-requests" in p for p in paths)
    assert any("work-orders" in p for p in paths)


def test_service_services_and_engines_importable():
    assert ServiceApplicationService is not None
    assert ServiceRequestService is not None
    assert WorkOrderService is not None
    assert ServiceExpenseService is not None
    assert ServiceRequestEngine is not None
    assert ServiceExpenseEngine is not None
