"""Asset API route handlers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from modules.asset.dependencies import (
    PaginationParams,
    extract_update_fields,
    get_db,
    get_pagination,
    paginate,
    require_permission,
)
from modules.asset.schemas import (
    AssetAssignmentCreate,
    AssetAssignmentResponse,
    AssetAssignmentUpdate,
    AssetAuditCreate,
    AssetAuditResponse,
    AssetAuditUpdate,
    AssetCategoryCreate,
    AssetCategoryResponse,
    AssetCategoryUpdate,
    AssetChecklistCreate,
    AssetChecklistResponse,
    AssetChecklistUpdate,
    AssetComponentCreate,
    AssetComponentResponse,
    AssetComponentUpdate,
    AssetCreate,
    AssetDepreciationCreate,
    AssetDepreciationResponse,
    AssetDepreciationUpdate,
    AssetDisposalCreate,
    AssetDisposalResponse,
    AssetDisposalUpdate,
    AssetDocumentCreate,
    AssetDocumentResponse,
    AssetDocumentUpdate,
    AssetInsuranceCreate,
    AssetInsuranceResponse,
    AssetInsuranceUpdate,
    AssetLocationCreate,
    AssetLocationResponse,
    AssetLocationUpdate,
    AssetMaintenanceCreate,
    AssetMaintenanceResponse,
    AssetMaintenanceUpdate,
    AssetNotificationCreate,
    AssetNotificationResponse,
    AssetNotificationUpdate,
    AssetReportCreate,
    AssetReportResponse,
    AssetReportUpdate,
    AssetResponse,
    AssetRevaluationCreate,
    AssetRevaluationResponse,
    AssetRevaluationUpdate,
    AssetTransferCreate,
    AssetTransferResponse,
    AssetTransferUpdate,
    AssetUpdate,
    AssetWarrantyCreate,
    AssetWarrantyResponse,
    AssetWarrantyUpdate,
    FinancePostRequest,
    MaintenancePlanCreate,
    MaintenancePlanResponse,
    MaintenancePlanUpdate,
    MeterReadingCreate,
    MeterReadingResponse,
    MeterReadingUpdate,
    ServiceHistoryCreate,
    ServiceHistoryResponse,
    ServiceHistoryUpdate,
)
from modules.asset.service import (
    AssetAuditService,
    AssetCategoryService,
    AssetReportService,
    AssetService,
    AssignmentService,
    ChecklistService,
    ComponentService,
    DepreciationService,
    DisposalService,
    DocumentService,
    InsuranceService,
    LocationService,
    MaintenancePlanService,
    MaintenanceService,
    MeterReadingService,
    NotificationService,
    RevaluationService,
    ServiceHistoryService,
    TransferService,
    WarrantyService,
)
from modules.foundation.domain.value_objects import TenantContext
from shared.schemas import APIResponse

asset_categories_router = APIRouter(prefix="/asset-categories", tags=["Asset — AssetCategory"])

@asset_categories_router.get("", response_model=APIResponse[list[AssetCategoryResponse]])
def list_asset_categories(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.category:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = AssetCategoryService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_categories_router.get("/{row_id}", response_model=APIResponse[AssetCategoryResponse])
def get_asset_categories(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.category:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AssetCategoryService(db).get(ctx, row_id))

@asset_categories_router.post("", response_model=APIResponse[AssetCategoryResponse])
def create_asset_categories(
    body: AssetCategoryCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.category:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=AssetCategoryService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_categories_router.patch("/{row_id}", response_model=APIResponse[AssetCategoryResponse])
def update_asset_categories(
    row_id: UUID,
    body: AssetCategoryUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.category:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=AssetCategoryService(db).update(ctx, row_id, **extract_update_fields(body)))

assets_router = APIRouter(prefix="/assets", tags=["Asset — Asset"])

@assets_router.get("", response_model=APIResponse[list[AssetResponse]])
def list_assets(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = AssetService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@assets_router.get("/{row_id}", response_model=APIResponse[AssetResponse])
def get_assets(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AssetService(db).get(ctx, row_id))

@assets_router.post("", response_model=APIResponse[AssetResponse])
def create_assets(
    body: AssetCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=AssetService(db).create(ctx, branch_id=body.branch_id, **body.model_dump(exclude={'branch_id'}, exclude_none=True)))

@assets_router.patch("/{row_id}", response_model=APIResponse[AssetResponse])
def update_assets(
    row_id: UUID,
    body: AssetUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=AssetService(db).update(ctx, row_id, **extract_update_fields(body)))

@assets_router.post("/{row_id}/submit", response_model=APIResponse[AssetResponse])
def submit_assets(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="submit", data=AssetService(db).submit(ctx, row_id))

@assets_router.post("/{row_id}/approve", response_model=APIResponse[AssetResponse])
def approve_assets(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="approve", data=AssetService(db).approve(ctx, row_id))

asset_components_router = APIRouter(prefix="/asset-components", tags=["Asset — AssetComponent"])

@asset_components_router.get("", response_model=APIResponse[list[AssetComponentResponse]])
def list_asset_components(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = ComponentService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_components_router.get("/{row_id}", response_model=APIResponse[AssetComponentResponse])
def get_asset_components(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ComponentService(db).get(ctx, row_id))

@asset_components_router.post("", response_model=APIResponse[AssetComponentResponse])
def create_asset_components(
    body: AssetComponentCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=ComponentService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_components_router.patch("/{row_id}", response_model=APIResponse[AssetComponentResponse])
def update_asset_components(
    row_id: UUID,
    body: AssetComponentUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=ComponentService(db).update(ctx, row_id, **extract_update_fields(body)))

asset_assignments_router = APIRouter(prefix="/asset-assignments", tags=["Asset — AssetAssignment"])

@asset_assignments_router.get("", response_model=APIResponse[list[AssetAssignmentResponse]])
def list_asset_assignments(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.assignment:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = AssignmentService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_assignments_router.get("/{row_id}", response_model=APIResponse[AssetAssignmentResponse])
def get_asset_assignments(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.assignment:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AssignmentService(db).get(ctx, row_id))

@asset_assignments_router.post("", response_model=APIResponse[AssetAssignmentResponse])
def create_asset_assignments(
    body: AssetAssignmentCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.assignment:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=AssignmentService(db).create(ctx, branch_id=body.branch_id, **body.model_dump(exclude={'branch_id'}, exclude_none=True)))

@asset_assignments_router.patch("/{row_id}", response_model=APIResponse[AssetAssignmentResponse])
def update_asset_assignments(
    row_id: UUID,
    body: AssetAssignmentUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.assignment:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=AssignmentService(db).update(ctx, row_id, **extract_update_fields(body)))

@asset_assignments_router.post("/{row_id}/submit", response_model=APIResponse[AssetAssignmentResponse])
def submit_asset_assignments(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.assignment:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="submit", data=AssignmentService(db).submit(ctx, row_id))

@asset_assignments_router.post("/{row_id}/approve", response_model=APIResponse[AssetAssignmentResponse])
def approve_asset_assignments(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.assignment:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="approve", data=AssignmentService(db).approve(ctx, row_id))

@asset_assignments_router.post("/{row_id}/return", response_model=APIResponse[AssetAssignmentResponse])
def return_asset_assignments(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.assignment:return"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="return", data=AssignmentService(db).return_assignment(ctx, row_id))

asset_transfers_router = APIRouter(prefix="/asset-transfers", tags=["Asset — AssetTransfer"])

@asset_transfers_router.get("", response_model=APIResponse[list[AssetTransferResponse]])
def list_asset_transfers(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.transfer:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = TransferService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_transfers_router.get("/{row_id}", response_model=APIResponse[AssetTransferResponse])
def get_asset_transfers(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.transfer:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=TransferService(db).get(ctx, row_id))

@asset_transfers_router.post("", response_model=APIResponse[AssetTransferResponse])
def create_asset_transfers(
    body: AssetTransferCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.transfer:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=TransferService(db).create(ctx, branch_id=body.branch_id, **body.model_dump(exclude={'branch_id'}, exclude_none=True)))

@asset_transfers_router.patch("/{row_id}", response_model=APIResponse[AssetTransferResponse])
def update_asset_transfers(
    row_id: UUID,
    body: AssetTransferUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.transfer:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=TransferService(db).update(ctx, row_id, **extract_update_fields(body)))

@asset_transfers_router.post("/{row_id}/complete", response_model=APIResponse[AssetTransferResponse])
def complete_asset_transfers(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.transfer:complete"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="complete", data=TransferService(db).complete(ctx, row_id))

asset_locations_router = APIRouter(prefix="/asset-locations", tags=["Asset — AssetLocation"])

@asset_locations_router.get("", response_model=APIResponse[list[AssetLocationResponse]])
def list_asset_locations(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.location:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = LocationService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_locations_router.get("/{row_id}", response_model=APIResponse[AssetLocationResponse])
def get_asset_locations(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.location:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=LocationService(db).get(ctx, row_id))

@asset_locations_router.post("", response_model=APIResponse[AssetLocationResponse])
def create_asset_locations(
    body: AssetLocationCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.location:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=LocationService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_locations_router.patch("/{row_id}", response_model=APIResponse[AssetLocationResponse])
def update_asset_locations(
    row_id: UUID,
    body: AssetLocationUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.location:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=LocationService(db).update(ctx, row_id, **extract_update_fields(body)))

asset_warranties_router = APIRouter(prefix="/asset-warranties", tags=["Asset — AssetWarranty"])

@asset_warranties_router.get("", response_model=APIResponse[list[AssetWarrantyResponse]])
def list_asset_warranties(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.warranty:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = WarrantyService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_warranties_router.get("/{row_id}", response_model=APIResponse[AssetWarrantyResponse])
def get_asset_warranties(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.warranty:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=WarrantyService(db).get(ctx, row_id))

@asset_warranties_router.post("", response_model=APIResponse[AssetWarrantyResponse])
def create_asset_warranties(
    body: AssetWarrantyCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.warranty:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=WarrantyService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_warranties_router.patch("/{row_id}", response_model=APIResponse[AssetWarrantyResponse])
def update_asset_warranties(
    row_id: UUID,
    body: AssetWarrantyUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.warranty:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=WarrantyService(db).update(ctx, row_id, **extract_update_fields(body)))

asset_insurances_router = APIRouter(prefix="/asset-insurances", tags=["Asset — AssetInsurance"])

@asset_insurances_router.get("", response_model=APIResponse[list[AssetInsuranceResponse]])
def list_asset_insurances(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.insurance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = InsuranceService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_insurances_router.get("/{row_id}", response_model=APIResponse[AssetInsuranceResponse])
def get_asset_insurances(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.insurance:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=InsuranceService(db).get(ctx, row_id))

@asset_insurances_router.post("", response_model=APIResponse[AssetInsuranceResponse])
def create_asset_insurances(
    body: AssetInsuranceCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.insurance:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=InsuranceService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_insurances_router.patch("/{row_id}", response_model=APIResponse[AssetInsuranceResponse])
def update_asset_insurances(
    row_id: UUID,
    body: AssetInsuranceUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.insurance:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=InsuranceService(db).update(ctx, row_id, **extract_update_fields(body)))

maintenance_plans_router = APIRouter(prefix="/maintenance-plans", tags=["Asset — MaintenancePlan"])

@maintenance_plans_router.get("", response_model=APIResponse[list[MaintenancePlanResponse]])
def list_maintenance_plans(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = MaintenancePlanService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@maintenance_plans_router.get("/{row_id}", response_model=APIResponse[MaintenancePlanResponse])
def get_maintenance_plans(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=MaintenancePlanService(db).get(ctx, row_id))

@maintenance_plans_router.post("", response_model=APIResponse[MaintenancePlanResponse])
def create_maintenance_plans(
    body: MaintenancePlanCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=MaintenancePlanService(db).create(ctx, **body.model_dump(exclude_none=True)))

@maintenance_plans_router.patch("/{row_id}", response_model=APIResponse[MaintenancePlanResponse])
def update_maintenance_plans(
    row_id: UUID,
    body: MaintenancePlanUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=MaintenancePlanService(db).update(ctx, row_id, **extract_update_fields(body)))

asset_maintenances_router = APIRouter(prefix="/asset-maintenances", tags=["Asset — AssetMaintenance"])

@asset_maintenances_router.get("", response_model=APIResponse[list[AssetMaintenanceResponse]])
def list_asset_maintenances(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = MaintenanceService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_maintenances_router.get("/{row_id}", response_model=APIResponse[AssetMaintenanceResponse])
def get_asset_maintenances(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=MaintenanceService(db).get(ctx, row_id))

@asset_maintenances_router.post("", response_model=APIResponse[AssetMaintenanceResponse])
def create_asset_maintenances(
    body: AssetMaintenanceCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=MaintenanceService(db).create(ctx, branch_id=body.branch_id, **body.model_dump(exclude={'branch_id'}, exclude_none=True)))

@asset_maintenances_router.patch("/{row_id}", response_model=APIResponse[AssetMaintenanceResponse])
def update_asset_maintenances(
    row_id: UUID,
    body: AssetMaintenanceUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=MaintenanceService(db).update(ctx, row_id, **extract_update_fields(body)))

@asset_maintenances_router.post("/{row_id}/submit", response_model=APIResponse[AssetMaintenanceResponse])
def submit_asset_maintenances(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="submit", data=MaintenanceService(db).submit(ctx, row_id))

@asset_maintenances_router.post("/{row_id}/approve", response_model=APIResponse[AssetMaintenanceResponse])
def approve_asset_maintenances(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="approve", data=MaintenanceService(db).approve(ctx, row_id))

@asset_maintenances_router.post("/{row_id}/complete", response_model=APIResponse[AssetMaintenanceResponse])
def complete_asset_maintenances(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:complete"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="complete", data=MaintenanceService(db).complete(ctx, row_id))

service_histories_router = APIRouter(prefix="/service-histories", tags=["Asset — ServiceHistory"])

@service_histories_router.get("", response_model=APIResponse[list[ServiceHistoryResponse]])
def list_service_histories(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = ServiceHistoryService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@service_histories_router.get("/{row_id}", response_model=APIResponse[ServiceHistoryResponse])
def get_service_histories(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ServiceHistoryService(db).get(ctx, row_id))

@service_histories_router.post("", response_model=APIResponse[ServiceHistoryResponse])
def create_service_histories(
    body: ServiceHistoryCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=ServiceHistoryService(db).create(ctx, **body.model_dump(exclude_none=True)))

@service_histories_router.patch("/{row_id}", response_model=APIResponse[ServiceHistoryResponse])
def update_service_histories(
    row_id: UUID,
    body: ServiceHistoryUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.maintenance:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=ServiceHistoryService(db).update(ctx, row_id, **extract_update_fields(body)))

asset_depreciations_router = APIRouter(prefix="/asset-depreciations", tags=["Asset — AssetDepreciation"])

@asset_depreciations_router.get("", response_model=APIResponse[list[AssetDepreciationResponse]])
def list_asset_depreciations(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.depreciation:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = DepreciationService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_depreciations_router.get("/{row_id}", response_model=APIResponse[AssetDepreciationResponse])
def get_asset_depreciations(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.depreciation:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=DepreciationService(db).get(ctx, row_id))

@asset_depreciations_router.post("", response_model=APIResponse[AssetDepreciationResponse])
def create_asset_depreciations(
    body: AssetDepreciationCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.depreciation:calculate"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=DepreciationService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_depreciations_router.patch("/{row_id}", response_model=APIResponse[AssetDepreciationResponse])
def update_asset_depreciations(
    row_id: UUID,
    body: AssetDepreciationUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.depreciation:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=DepreciationService(db).update(ctx, row_id, **extract_update_fields(body)))

@asset_depreciations_router.post("/{row_id}/calculate", response_model=APIResponse[AssetDepreciationResponse])
def calculate_asset_depreciations(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.depreciation:calculate"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="calculate", data=DepreciationService(db).calculate(ctx, row_id))

@asset_depreciations_router.post("/{row_id}/post", response_model=APIResponse[AssetDepreciationResponse])
def post_asset_depreciations(
    row_id: UUID,
    body: FinancePostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.depreciation:post"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = DepreciationService(db).post(
        ctx,
        row_id,
        debit_account_id=body.debit_account_id,
        credit_account_id=body.credit_account_id,
        fiscal_year_id=body.fiscal_year_id,
    )
    return APIResponse(message="Posted", data=data)

asset_disposals_router = APIRouter(prefix="/asset-disposals", tags=["Asset — AssetDisposal"])

@asset_disposals_router.get("", response_model=APIResponse[list[AssetDisposalResponse]])
def list_asset_disposals(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.disposal:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = DisposalService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_disposals_router.get("/{row_id}", response_model=APIResponse[AssetDisposalResponse])
def get_asset_disposals(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.disposal:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=DisposalService(db).get(ctx, row_id))

@asset_disposals_router.post("", response_model=APIResponse[AssetDisposalResponse])
def create_asset_disposals(
    body: AssetDisposalCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.disposal:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=DisposalService(db).create(ctx, branch_id=body.branch_id, **body.model_dump(exclude={'branch_id'}, exclude_none=True)))

@asset_disposals_router.patch("/{row_id}", response_model=APIResponse[AssetDisposalResponse])
def update_asset_disposals(
    row_id: UUID,
    body: AssetDisposalUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.disposal:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=DisposalService(db).update(ctx, row_id, **extract_update_fields(body)))

@asset_disposals_router.post("/{row_id}/submit", response_model=APIResponse[AssetDisposalResponse])
def submit_asset_disposals(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.disposal:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="submit", data=DisposalService(db).submit(ctx, row_id))

@asset_disposals_router.post("/{row_id}/approve", response_model=APIResponse[AssetDisposalResponse])
def approve_asset_disposals(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.disposal:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="approve", data=DisposalService(db).approve(ctx, row_id))

@asset_disposals_router.post("/{row_id}/post", response_model=APIResponse[AssetDisposalResponse])
def post_asset_disposals(
    row_id: UUID,
    body: FinancePostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.disposal:post"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = DisposalService(db).post(
        ctx,
        row_id,
        debit_account_id=body.debit_account_id,
        credit_account_id=body.credit_account_id,
        fiscal_year_id=body.fiscal_year_id,
    )
    return APIResponse(message="Posted", data=data)

asset_revaluations_router = APIRouter(prefix="/asset-revaluations", tags=["Asset — AssetRevaluation"])

@asset_revaluations_router.get("", response_model=APIResponse[list[AssetRevaluationResponse]])
def list_asset_revaluations(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.revaluation:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = RevaluationService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_revaluations_router.get("/{row_id}", response_model=APIResponse[AssetRevaluationResponse])
def get_asset_revaluations(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.revaluation:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=RevaluationService(db).get(ctx, row_id))

@asset_revaluations_router.post("", response_model=APIResponse[AssetRevaluationResponse])
def create_asset_revaluations(
    body: AssetRevaluationCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.revaluation:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=RevaluationService(db).create(ctx, branch_id=body.branch_id, **body.model_dump(exclude={'branch_id'}, exclude_none=True)))

@asset_revaluations_router.patch("/{row_id}", response_model=APIResponse[AssetRevaluationResponse])
def update_asset_revaluations(
    row_id: UUID,
    body: AssetRevaluationUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.revaluation:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=RevaluationService(db).update(ctx, row_id, **extract_update_fields(body)))

@asset_revaluations_router.post("/{row_id}/submit", response_model=APIResponse[AssetRevaluationResponse])
def submit_asset_revaluations(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.revaluation:submit"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="submit", data=RevaluationService(db).submit(ctx, row_id))

@asset_revaluations_router.post("/{row_id}/approve", response_model=APIResponse[AssetRevaluationResponse])
def approve_asset_revaluations(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.revaluation:approve"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="approve", data=RevaluationService(db).approve(ctx, row_id))

@asset_revaluations_router.post("/{row_id}/post", response_model=APIResponse[AssetRevaluationResponse])
def post_asset_revaluations(
    row_id: UUID,
    body: FinancePostRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.revaluation:post"))],
    db: Annotated[Session, Depends(get_db)],
):
    data = RevaluationService(db).post(
        ctx,
        row_id,
        debit_account_id=body.debit_account_id,
        credit_account_id=body.credit_account_id,
        fiscal_year_id=body.fiscal_year_id,
    )
    return APIResponse(message="Posted", data=data)

asset_audits_router = APIRouter(prefix="/asset-audits", tags=["Asset — AssetAudit"])

@asset_audits_router.get("", response_model=APIResponse[list[AssetAuditResponse]])
def list_asset_audits(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.audit:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = AssetAuditService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_audits_router.get("/{row_id}", response_model=APIResponse[AssetAuditResponse])
def get_asset_audits(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.audit:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AssetAuditService(db).get(ctx, row_id))

@asset_audits_router.post("", response_model=APIResponse[AssetAuditResponse])
def create_asset_audits(
    body: AssetAuditCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.audit:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=AssetAuditService(db).create(ctx, branch_id=body.branch_id, **body.model_dump(exclude={'branch_id'}, exclude_none=True)))

@asset_audits_router.patch("/{row_id}", response_model=APIResponse[AssetAuditResponse])
def update_asset_audits(
    row_id: UUID,
    body: AssetAuditUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.audit:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=AssetAuditService(db).update(ctx, row_id, **extract_update_fields(body)))

@asset_audits_router.post("/{row_id}/complete", response_model=APIResponse[AssetAuditResponse])
def complete_asset_audits(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.audit:complete"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="complete", data=AssetAuditService(db).complete(ctx, row_id))

asset_documents_router = APIRouter(prefix="/asset-documents", tags=["Asset — AssetDocument"])

@asset_documents_router.get("", response_model=APIResponse[list[AssetDocumentResponse]])
def list_asset_documents(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.document:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = DocumentService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_documents_router.get("/{row_id}", response_model=APIResponse[AssetDocumentResponse])
def get_asset_documents(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.document:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=DocumentService(db).get(ctx, row_id))

@asset_documents_router.post("", response_model=APIResponse[AssetDocumentResponse])
def create_asset_documents(
    body: AssetDocumentCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.document:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=DocumentService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_documents_router.patch("/{row_id}", response_model=APIResponse[AssetDocumentResponse])
def update_asset_documents(
    row_id: UUID,
    body: AssetDocumentUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.document:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=DocumentService(db).update(ctx, row_id, **extract_update_fields(body)))

asset_checklists_router = APIRouter(prefix="/asset-checklists", tags=["Asset — AssetChecklist"])

@asset_checklists_router.get("", response_model=APIResponse[list[AssetChecklistResponse]])
def list_asset_checklists(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.checklist:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = ChecklistService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_checklists_router.get("/{row_id}", response_model=APIResponse[AssetChecklistResponse])
def get_asset_checklists(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.checklist:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ChecklistService(db).get(ctx, row_id))

@asset_checklists_router.post("", response_model=APIResponse[AssetChecklistResponse])
def create_asset_checklists(
    body: AssetChecklistCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.checklist:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=ChecklistService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_checklists_router.patch("/{row_id}", response_model=APIResponse[AssetChecklistResponse])
def update_asset_checklists(
    row_id: UUID,
    body: AssetChecklistUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.checklist:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=ChecklistService(db).update(ctx, row_id, **extract_update_fields(body)))

meter_readings_router = APIRouter(prefix="/meter-readings", tags=["Asset — MeterReading"])

@meter_readings_router.get("", response_model=APIResponse[list[MeterReadingResponse]])
def list_meter_readings(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.meter:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = MeterReadingService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@meter_readings_router.get("/{row_id}", response_model=APIResponse[MeterReadingResponse])
def get_meter_readings(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.meter:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=MeterReadingService(db).get(ctx, row_id))

@meter_readings_router.post("", response_model=APIResponse[MeterReadingResponse])
def create_meter_readings(
    body: MeterReadingCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.meter:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=MeterReadingService(db).create(ctx, **body.model_dump(exclude_none=True)))

@meter_readings_router.patch("/{row_id}", response_model=APIResponse[MeterReadingResponse])
def update_meter_readings(
    row_id: UUID,
    body: MeterReadingUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.meter:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=MeterReadingService(db).update(ctx, row_id, **extract_update_fields(body)))

asset_notifications_router = APIRouter(prefix="/asset-notifications", tags=["Asset — AssetNotification"])

@asset_notifications_router.get("", response_model=APIResponse[list[AssetNotificationResponse]])
def list_asset_notifications(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = NotificationService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@asset_notifications_router.get("/{row_id}", response_model=APIResponse[AssetNotificationResponse])
def get_asset_notifications(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=NotificationService(db).get(ctx, row_id))

@asset_notifications_router.post("", response_model=APIResponse[AssetNotificationResponse])
def create_asset_notifications(
    body: AssetNotificationCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=NotificationService(db).create(ctx, **body.model_dump(exclude_none=True)))

@asset_notifications_router.patch("/{row_id}", response_model=APIResponse[AssetNotificationResponse])
def update_asset_notifications(
    row_id: UUID,
    body: AssetNotificationUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.asset:update"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=NotificationService(db).update(ctx, row_id, **extract_update_fields(body)))

reports_router = APIRouter(prefix="/reports", tags=["Asset — AssetReport"])

@reports_router.get("", response_model=APIResponse[list[AssetReportResponse]])
def list_reports(
    ctx: Annotated[TenantContext, Depends(require_permission("asset.report:read"))],
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination)],
    company_id: UUID | None = None,
):
    items = AssetReportService(db).list(ctx, company_id=company_id)
    return APIResponse(message="OK", data=paginate(items, pagination))

@reports_router.get("/{row_id}", response_model=APIResponse[AssetReportResponse])
def get_reports(
    row_id: UUID,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.report:read"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=AssetReportService(db).get(ctx, row_id))

@reports_router.post("", response_model=APIResponse[AssetReportResponse])
def create_reports(
    body: AssetReportCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.report:export"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Created", data=AssetReportService(db).create(ctx, **body.model_dump(exclude_none=True)))

@reports_router.patch("/{row_id}", response_model=APIResponse[AssetReportResponse])
def update_reports(
    row_id: UUID,
    body: AssetReportUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("asset.report:export"))],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="Updated", data=AssetReportService(db).update(ctx, row_id, **extract_update_fields(body)))

