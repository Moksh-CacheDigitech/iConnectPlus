"""Service rate contracts / visit plans, and multi-site delivery project trackers."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_any_permission, require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.procurement.schemas import (
    DeliveryProjectCreate,
    DeliveryProjectDetailResponse,
    DeliveryProjectResponse,
    DeliveryProjectUpdate,
    DeliverySiteInput,
    DeliverySiteResponse,
    DeliveryTrackerImportRequest,
    DeliveryTrackerImportResponse,
    PublicTrackerResponse,
    ServicePlanCreate,
    ServicePlanResponse,
    ServiceRateContractCreate,
    ServiceRateContractResponse,
    ServiceRateContractUpdate,
    ServiceVisitCreate,
    ServiceVisitResponse,
)
from modules.procurement.service.delivery_project_service import DeliveryProjectService
from modules.procurement.service.service_contract_service import ServiceContractService
from security.public_routes import optional_authentication
from shared.schemas import APIResponse

service_projects_router = APIRouter(prefix="/scm", tags=["Procurement - Service POs & delivery projects"])
public_project_tracking_router = APIRouter(prefix="/public/project-tracking", tags=["Public - Project Tracking"])

_READ = require_any_permission("procurement.order:read", "crm.ovf:read")
_PLAN = require_any_permission("procurement.order:create", "crm.ovf:update")
_VISIT = require_any_permission("procurement.order:update", "crm.ovf:read")


# -- rate contracts -------------------------------------------------------------
@service_projects_router.get("/service-contracts", response_model=APIResponse[list[ServiceRateContractResponse]])
def list_service_contracts(
    ctx: Annotated[TenantContext, Depends(_READ)],
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = False,
):
    rows = ServiceContractService(db).list_contracts(ctx, active_only=active_only)
    return APIResponse(message="OK", data=[ServiceRateContractResponse.model_validate(r) for r in rows])


@service_projects_router.post("/service-contracts", response_model=APIResponse[ServiceRateContractResponse])
def create_service_contract(
    body: ServiceRateContractCreate,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.order:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ServiceContractService(db).create_contract(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Rate contract created", data=ServiceRateContractResponse.model_validate(row))


@service_projects_router.patch(
    "/service-contracts/{contract_id}", response_model=APIResponse[ServiceRateContractResponse]
)
def update_service_contract(
    contract_id: UUID,
    body: ServiceRateContractUpdate,
    ctx: Annotated[TenantContext, Depends(require_permission("procurement.order:create"))],
    db: Annotated[Session, Depends(get_db)],
):
    row = ServiceContractService(db).update_contract(ctx, contract_id, **body.model_dump(exclude_unset=True))
    db.commit()
    return APIResponse(message="Rate contract updated", data=ServiceRateContractResponse.model_validate(row))


# -- service plans / visits ---------------------------------------------------------
@service_projects_router.get("/service-plans", response_model=APIResponse[list[ServicePlanResponse]])
def list_service_plans(
    ovf_id: UUID,
    ctx: Annotated[TenantContext, Depends(_READ)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=ServiceContractService(db).list_plans(ctx, ovf_id))


@service_projects_router.post("/service-plans", response_model=APIResponse[ServicePlanResponse])
def create_service_plan(
    body: ServicePlanCreate,
    ctx: Annotated[TenantContext, Depends(_PLAN)],
    db: Annotated[Session, Depends(get_db)],
):
    """Price projected visits off a rate contract; adds vendor lines while the OVF is a draft."""
    row = ServiceContractService(db).create_plan(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Service plan created", data=row)


@service_projects_router.post("/service-plans/{plan_id}/close", response_model=APIResponse[ServicePlanResponse])
def close_service_plan(
    plan_id: UUID,
    ctx: Annotated[TenantContext, Depends(_PLAN)],
    db: Annotated[Session, Depends(get_db)],
):
    row = ServiceContractService(db).close_plan(ctx, plan_id)
    db.commit()
    return APIResponse(message="Service plan closed", data=row)


@service_projects_router.get(
    "/service-plans/{plan_id}/visits", response_model=APIResponse[list[ServiceVisitResponse]]
)
def list_service_visits(
    plan_id: UUID,
    ctx: Annotated[TenantContext, Depends(_READ)],
    db: Annotated[Session, Depends(get_db)],
):
    rows = ServiceContractService(db).list_visits(ctx, plan_id)
    return APIResponse(message="OK", data=[ServiceVisitResponse.model_validate(r) for r in rows])


@service_projects_router.post("/service-plans/{plan_id}/visits", response_model=APIResponse[ServiceVisitResponse])
def log_service_visit(
    plan_id: UUID,
    body: ServiceVisitCreate,
    ctx: Annotated[TenantContext, Depends(_VISIT)],
    db: Annotated[Session, Depends(get_db)],
):
    """Visits beyond the projection are raised on the OVF as execution expenses."""
    row = ServiceContractService(db).log_visit(ctx, plan_id, **body.model_dump())
    db.commit()
    return APIResponse(message="Visit logged", data=ServiceVisitResponse.model_validate(row))


@service_projects_router.post("/service-visits/{visit_id}/cancel", response_model=APIResponse[ServiceVisitResponse])
def cancel_service_visit(
    visit_id: UUID,
    ctx: Annotated[TenantContext, Depends(_VISIT)],
    db: Annotated[Session, Depends(get_db)],
):
    row = ServiceContractService(db).cancel_visit(ctx, visit_id)
    db.commit()
    return APIResponse(message="Visit cancelled", data=ServiceVisitResponse.model_validate(row))


# -- delivery projects ------------------------------------------------------------
@service_projects_router.get("/delivery-projects", response_model=APIResponse[list[DeliveryProjectResponse]])
def list_delivery_projects(
    ctx: Annotated[TenantContext, Depends(_READ)],
    db: Annotated[Session, Depends(get_db)],
    company_account_id: UUID | None = None,
):
    return APIResponse(
        message="OK",
        data=DeliveryProjectService(db).list_projects(ctx, company_account_id=company_account_id),
    )


@service_projects_router.post("/delivery-projects", response_model=APIResponse[DeliveryProjectDetailResponse])
def create_delivery_project(
    body: DeliveryProjectCreate,
    ctx: Annotated[TenantContext, Depends(_PLAN)],
    db: Annotated[Session, Depends(get_db)],
):
    row = DeliveryProjectService(db).create_project(ctx, **body.model_dump())
    db.commit()
    return APIResponse(message="Delivery project created", data=row)


@service_projects_router.get(
    "/delivery-projects/{project_id}", response_model=APIResponse[DeliveryProjectDetailResponse]
)
def get_delivery_project(
    project_id: UUID,
    ctx: Annotated[TenantContext, Depends(_READ)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(message="OK", data=DeliveryProjectService(db).get_project(ctx, project_id))


@service_projects_router.patch(
    "/delivery-projects/{project_id}", response_model=APIResponse[DeliveryProjectDetailResponse]
)
def update_delivery_project(
    project_id: UUID,
    body: DeliveryProjectUpdate,
    ctx: Annotated[TenantContext, Depends(_PLAN)],
    db: Annotated[Session, Depends(get_db)],
):
    row = DeliveryProjectService(db).update_project(ctx, project_id, **body.model_dump(exclude_unset=True))
    db.commit()
    return APIResponse(message="Project updated", data=row)


@service_projects_router.post(
    "/delivery-projects/{project_id}/sites", response_model=APIResponse[DeliverySiteResponse]
)
def add_delivery_site(
    project_id: UUID,
    body: DeliverySiteInput,
    ctx: Annotated[TenantContext, Depends(_VISIT)],
    db: Annotated[Session, Depends(get_db)],
):
    row = DeliveryProjectService(db).add_site(ctx, project_id, **body.model_dump(exclude_none=True))
    db.commit()
    return APIResponse(message="Site added", data=row)


@service_projects_router.post(
    "/delivery-projects/{project_id}/import-from-opportunity", response_model=APIResponse[dict[str, int]]
)
def import_sites_from_opportunity(
    project_id: UUID,
    ctx: Annotated[TenantContext, Depends(_PLAN)],
    db: Annotated[Session, Depends(get_db)],
):
    row = DeliveryProjectService(db).import_sites_from_opportunity(ctx, project_id)
    db.commit()
    return APIResponse(message=f"{row['created']} site(s) added from the deal's OVFs", data=row)


@service_projects_router.patch("/delivery-sites/{site_id}", response_model=APIResponse[DeliverySiteResponse])
def update_delivery_site(
    site_id: UUID,
    body: DeliverySiteInput,
    ctx: Annotated[TenantContext, Depends(_VISIT)],
    db: Annotated[Session, Depends(get_db)],
):
    row = DeliveryProjectService(db).update_site(ctx, site_id, **body.model_dump(exclude_unset=True))
    db.commit()
    return APIResponse(message="Site updated", data=row)


@service_projects_router.delete("/delivery-sites/{site_id}", response_model=APIResponse[dict[str, str]])
def delete_delivery_site(
    site_id: UUID,
    ctx: Annotated[TenantContext, Depends(_PLAN)],
    db: Annotated[Session, Depends(get_db)],
):
    DeliveryProjectService(db).delete_site(ctx, site_id)
    db.commit()
    return APIResponse(message="Site removed", data={"id": str(site_id)})


@service_projects_router.get("/delivery-projects/{project_id}/excel")
def export_delivery_tracker(
    project_id: UUID,
    ctx: Annotated[TenantContext, Depends(_READ)],
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    file_name, content = DeliveryProjectService(db).export_excel(ctx, project_id)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
    )


@service_projects_router.post(
    "/delivery-projects/{project_id}/excel", response_model=APIResponse[DeliveryTrackerImportResponse]
)
def import_delivery_tracker(
    project_id: UUID,
    body: DeliveryTrackerImportRequest,
    ctx: Annotated[TenantContext, Depends(_VISIT)],
    db: Annotated[Session, Depends(get_db)],
):
    """Rows with a Site Key update that site; other rows match on Customer PO + Site Code or add a site."""
    row = DeliveryProjectService(db).import_excel(ctx, project_id, content_base64=body.content_base64)
    db.commit()
    return APIResponse(message="Tracker imported", data=row)


# -- public ---------------------------------------------------------------------------
@public_project_tracking_router.get("/{token}", response_model=APIResponse[PublicTrackerResponse])
def public_project_tracker(
    token: str,
    db: Annotated[Session, Depends(get_db)],
    _public: Annotated[None, Depends(optional_authentication)],
):
    return APIResponse(message="OK", data=DeliveryProjectService(db).public_view(token))
