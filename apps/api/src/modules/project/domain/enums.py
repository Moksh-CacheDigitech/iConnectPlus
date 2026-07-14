"""Project domain enums per ERD_14 §11."""

from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class ProjectPhaseStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectMilestoneStatus(str, Enum):
    PLANNED = "planned"
    ACHIEVED = "achieved"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class ProjectTaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SUBMITTED = "submitted"
    APPROVED = "approved"


class TaskDependencyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class TaskAssignmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    REMOVED = "removed"


class TimesheetStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class TimesheetEntryStatus(str, Enum):
    DRAFT = "draft"
    LOCKED = "locked"
    CANCELLED = "cancelled"


class ResourcePlanStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ResourceAllocationStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectBudgetStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    CLOSED = "closed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ProjectCostStatus(str, Enum):
    DRAFT = "draft"
    POSTED = "posted"
    FAILED = "failed"
    REVERSED = "reversed"
    CANCELLED = "cancelled"


class ProjectIssueStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ProjectRiskStatus(str, Enum):
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    ACCEPTED = "accepted"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ChangeRequestStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class ProjectDocumentStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class ProjectCommentStatus(str, Enum):
    ACTIVE = "active"
    EDITED = "edited"
    DELETED_SOFT = "deleted_soft"


class ProjectNotificationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ProjectReportStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"


class PrjEntityType(str, Enum):
    PROJECT = "project"
    PROJECT_TASK = "project_task"
    TIMESHEET = "timesheet"
    RESOURCE_PLAN = "resource_plan"
    PROJECT_BUDGET = "project_budget"
    PROJECT_COST = "project_cost"
    PROJECT_ISSUE = "project_issue"
    PROJECT_RISK = "project_risk"
    CHANGE_REQUEST = "change_request"
    PROJECT_REPORT = "project_report"


CODE_PREFIXES: dict[PrjEntityType, tuple[str, int, bool]] = {
    PrjEntityType.PROJECT: ("PRJ-", 6, True),
    PrjEntityType.PROJECT_TASK: ("TASK-", 6, True),
    PrjEntityType.TIMESHEET: ("TS-", 6, True),
    PrjEntityType.RESOURCE_PLAN: ("RPLAN-", 6, True),
    PrjEntityType.PROJECT_BUDGET: ("PBUD-", 6, True),
    PrjEntityType.PROJECT_COST: ("PCOST-", 6, True),
    PrjEntityType.PROJECT_ISSUE: ("PISS-", 6, True),
    PrjEntityType.PROJECT_RISK: ("PRISK-", 6, True),
    PrjEntityType.CHANGE_REQUEST: ("PCR-", 6, True),
    PrjEntityType.PROJECT_REPORT: ("PRPT-", 6, True),
}
