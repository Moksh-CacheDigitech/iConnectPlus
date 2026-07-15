"""Service application service facade."""

from sqlalchemy.orm import Session

from modules.service.service.integration_service import ServiceIntegrationService
from modules.service.service.service_assignment_service import ServiceAssignmentService
from modules.service.service.service_category_service import ServiceCategoryService
from modules.service.service.service_checklist_service import ServiceChecklistService
from modules.service.service.service_contract_service import ServiceContractService
from modules.service.service.service_document_service import ServiceDocumentService
from modules.service.service.service_escalation_service import ServiceEscalationService
from modules.service.service.service_expense_service import ServiceExpenseService
from modules.service.service.service_feedback_service import ServiceFeedbackService
from modules.service.service.service_material_service import ServiceMaterialService
from modules.service.service.service_notification_service import ServiceNotificationService
from modules.service.service.service_report_service import ServiceReportService
from modules.service.service.service_request_service import ServiceRequestService
from modules.service.service.service_resolution_service import ServiceResolutionService
from modules.service.service.service_schedule_service import ServiceScheduleService
from modules.service.service.service_sla_service import ServiceSLAService
from modules.service.service.service_task_service import ServiceTaskService
from modules.service.service.service_ticket_service import ServiceTicketService
from modules.service.service.service_time_entry_service import ServiceTimeEntryService
from modules.service.service.service_visit_service import ServiceVisitService
from modules.service.service.work_order_service import WorkOrderService


class ServiceApplicationService:
    def __init__(self, db: Session) -> None:
        self.categories = ServiceCategoryService(db)
        self.requests = ServiceRequestService(db)
        self.tickets = ServiceTicketService(db)
        self.assignments = ServiceAssignmentService(db)
        self.schedules = ServiceScheduleService(db)
        self.work_orders = WorkOrderService(db)
        self.tasks = ServiceTaskService(db)
        self.checklists = ServiceChecklistService(db)
        self.visits = ServiceVisitService(db)
        self.materials = ServiceMaterialService(db)
        self.time_entries = ServiceTimeEntryService(db)
        self.expenses = ServiceExpenseService(db)
        self.slas = ServiceSLAService(db)
        self.escalations = ServiceEscalationService(db)
        self.feedback = ServiceFeedbackService(db)
        self.resolutions = ServiceResolutionService(db)
        self.documents = ServiceDocumentService(db)
        self.notifications = ServiceNotificationService(db)
        self.contracts = ServiceContractService(db)
        self.reports = ServiceReportService(db)
        self.integration = ServiceIntegrationService(db)
