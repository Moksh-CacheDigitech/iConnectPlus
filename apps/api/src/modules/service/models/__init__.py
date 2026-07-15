"""Service ORM models."""

from modules.service.models.service_assignment import SvcServiceAssignment
from modules.service.models.service_category import SvcServiceCategory
from modules.service.models.service_checklist import SvcServiceChecklist
from modules.service.models.service_contract import SvcServiceContract
from modules.service.models.service_document import SvcServiceDocument
from modules.service.models.service_escalation import SvcServiceEscalation
from modules.service.models.service_expense import SvcServiceExpense
from modules.service.models.service_feedback import SvcServiceFeedback
from modules.service.models.service_material import SvcServiceMaterial
from modules.service.models.service_notification import SvcServiceNotification
from modules.service.models.service_report import SvcServiceReport
from modules.service.models.service_request import SvcServiceRequest
from modules.service.models.service_resolution import SvcServiceResolution
from modules.service.models.service_schedule import SvcServiceSchedule
from modules.service.models.service_sla import SvcServiceSla
from modules.service.models.service_task import SvcServiceTask
from modules.service.models.service_ticket import SvcServiceTicket
from modules.service.models.service_time_entry import SvcServiceTimeEntry
from modules.service.models.service_visit import SvcServiceVisit
from modules.service.models.service_work_order import SvcServiceWorkOrder

__all__ = [
    "SvcServiceCategory",
    "SvcServiceRequest",
    "SvcServiceTicket",
    "SvcServiceAssignment",
    "SvcServiceSchedule",
    "SvcServiceWorkOrder",
    "SvcServiceTask",
    "SvcServiceChecklist",
    "SvcServiceVisit",
    "SvcServiceMaterial",
    "SvcServiceTimeEntry",
    "SvcServiceExpense",
    "SvcServiceSla",
    "SvcServiceEscalation",
    "SvcServiceFeedback",
    "SvcServiceResolution",
    "SvcServiceDocument",
    "SvcServiceNotification",
    "SvcServiceContract",
    "SvcServiceReport",
]
