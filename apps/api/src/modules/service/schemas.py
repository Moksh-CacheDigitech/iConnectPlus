"""Service Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ServiceCategoryCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceCategoryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceCategoryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceRequestCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceRequestUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceRequestResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceTicketCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceTicketUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceTicketResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceAssignmentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceAssignmentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceAssignmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceScheduleCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceScheduleUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceScheduleResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class WorkOrderCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class WorkOrderUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class WorkOrderResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceTaskCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceTaskUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceTaskResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceChecklistCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceChecklistUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceChecklistResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceVisitCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceVisitUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceVisitResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceMaterialCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceMaterialUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceMaterialResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceTimeEntryCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceTimeEntryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceTimeEntryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceExpenseCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceExpenseUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceExpenseResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceSlaCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceSlaUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceSlaResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceEscalationCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceEscalationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceEscalationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceFeedbackCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceFeedbackUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceFeedbackResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceResolutionCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceResolutionUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceResolutionResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceDocumentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceDocumentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceDocumentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceNotificationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceNotificationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceNotificationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceContractCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ServiceContractUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceContractResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceReportCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceReportUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceReportResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class FinancePostRequest(BaseModel):
    debit_account_id: UUID
    credit_account_id: UUID
    fiscal_year_id: UUID | None = None
