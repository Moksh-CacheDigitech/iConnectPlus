"""Project application service facade."""

from sqlalchemy.orm import Session

from modules.project.service.budget_service import BudgetService
from modules.project.service.change_request_service import ChangeRequestService
from modules.project.service.comment_service import CommentService
from modules.project.service.cost_service import CostService
from modules.project.service.document_service import DocumentService
from modules.project.service.integration_service import ProjectIntegrationService
from modules.project.service.issue_service import IssueService
from modules.project.service.milestone_service import MilestoneService
from modules.project.service.notification_service import NotificationService
from modules.project.service.phase_service import PhaseService
from modules.project.service.project_report_service import ProjectReportService
from modules.project.service.project_service import ProjectService
from modules.project.service.resource_allocation_service import ResourceAllocationService
from modules.project.service.resource_planning_service import ResourcePlanningService
from modules.project.service.risk_service import RiskService
from modules.project.service.status_history_service import StatusHistoryService
from modules.project.service.task_assignment_service import TaskAssignmentService
from modules.project.service.task_dependency_service import TaskDependencyService
from modules.project.service.task_service import TaskService
from modules.project.service.timesheet_entry_service import TimesheetEntryService
from modules.project.service.timesheet_service import TimesheetService


class ProjectApplicationService:
    def __init__(self, db: Session) -> None:
        self.projects = ProjectService(db)
        self.phases = PhaseService(db)
        self.milestones = MilestoneService(db)
        self.tasks = TaskService(db)
        self.dependencies = TaskDependencyService(db)
        self.assignments = TaskAssignmentService(db)
        self.timesheets = TimesheetService(db)
        self.timesheet_entries = TimesheetEntryService(db)
        self.resource_plans = ResourcePlanningService(db)
        self.resource_allocations = ResourceAllocationService(db)
        self.budgets = BudgetService(db)
        self.costs = CostService(db)
        self.issues = IssueService(db)
        self.risks = RiskService(db)
        self.change_requests = ChangeRequestService(db)
        self.documents = DocumentService(db)
        self.comments = CommentService(db)
        self.status_history = StatusHistoryService(db)
        self.notifications = NotificationService(db)
        self.reports = ProjectReportService(db)
        self.integration = ProjectIntegrationService(db)
