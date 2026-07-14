"""Project Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ProjectUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectPhaseCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectPhaseUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectPhaseResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectMilestoneCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectMilestoneUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectMilestoneResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectTaskCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ProjectTaskUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectTaskResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class TaskDependencyCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class TaskDependencyUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class TaskDependencyResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class TaskAssignmentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class TaskAssignmentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class TaskAssignmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class TimesheetCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class TimesheetUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class TimesheetResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class TimesheetEntryCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class TimesheetEntryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class TimesheetEntryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ResourcePlanCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ResourcePlanUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ResourcePlanResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ResourceAllocationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ResourceAllocationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ResourceAllocationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectBudgetCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectBudgetUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectBudgetResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectCostCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ProjectCostUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectCostResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectIssueCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectIssueUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectIssueResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectRiskCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectRiskUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectRiskResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ChangeRequestCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ChangeRequestUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ChangeRequestResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectDocumentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectDocumentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectDocumentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectCommentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectCommentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectCommentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectStatusHistoryCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectStatusHistoryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectStatusHistoryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectNotificationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectNotificationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectNotificationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectReportCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ProjectReportUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ProjectReportResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ProjectCostPostRequest(BaseModel):
    debit_account_id: UUID
    credit_account_id: UUID
    fiscal_year_id: UUID | None = None
