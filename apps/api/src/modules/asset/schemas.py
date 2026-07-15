"""Asset Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AssetCategoryCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetCategoryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetCategoryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class AssetUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetComponentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetComponentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetComponentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetAssignmentCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class AssetAssignmentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetAssignmentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetTransferCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class AssetTransferUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetTransferResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetLocationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetLocationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetLocationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetWarrantyCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetWarrantyUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetWarrantyResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetInsuranceCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetInsuranceUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetInsuranceResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class MaintenancePlanCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class MaintenancePlanUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class MaintenancePlanResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetMaintenanceCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class AssetMaintenanceUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetMaintenanceResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ServiceHistoryCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ServiceHistoryUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ServiceHistoryResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetDepreciationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetDepreciationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetDepreciationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetDisposalCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class AssetDisposalUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetDisposalResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetRevaluationCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class AssetRevaluationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetRevaluationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetAuditCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class AssetAuditUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetAuditResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetDocumentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetDocumentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetDocumentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetChecklistCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetChecklistUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetChecklistResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class MeterReadingCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class MeterReadingUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class MeterReadingResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetNotificationCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetNotificationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetNotificationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class AssetReportCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class AssetReportUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class AssetReportResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class FinancePostRequest(BaseModel):
    debit_account_id: UUID
    credit_account_id: UUID
    fiscal_year_id: UUID | None = None
