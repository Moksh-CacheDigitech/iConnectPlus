"""Settings router."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from modules.foundation.dependencies import require_permission
from modules.foundation.domain.value_objects import TenantContext
from modules.foundation.schemas import SettingUpsertRequest
from modules.foundation.service.setting_service import SettingService
from shared.schemas import APIResponse

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=APIResponse[list])
def list_settings(
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.setting:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[list]:
    settings = SettingService(db).list_settings(ctx.tenant_id)
    return APIResponse(message="Settings retrieved", data=[s.__dict__ for s in settings])


@router.get("/{setting_key}", response_model=APIResponse[dict])
def get_setting(
    setting_key: str,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.setting:read"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    setting = SettingService(db).get_setting(ctx.tenant_id, setting_key)
    return APIResponse(message="Setting retrieved", data=setting.__dict__)


@router.put("/{setting_key}", response_model=APIResponse[dict])
def upsert_setting(
    setting_key: str,
    body: SettingUpsertRequest,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.setting:update"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[dict]:
    setting = SettingService(db).upsert_setting(
        tenant_id=ctx.tenant_id,
        setting_key=setting_key,
        setting_value=body.setting_value,
        value_type=body.value_type,
        scope=body.scope,
        updated_by=ctx.user_id,
    )
    db.commit()
    return APIResponse(message="Setting updated", data=setting.__dict__)


@router.delete("/{setting_key}", response_model=APIResponse[None])
def delete_setting(
    setting_key: str,
    ctx: Annotated[TenantContext, Depends(require_permission("foundation.setting:delete"))],
    db: Annotated[Session, Depends(get_db)],
) -> APIResponse[None]:
    SettingService(db).delete_setting(ctx.tenant_id, setting_key, deleted_by=ctx.user_id)
    db.commit()
    return APIResponse(message="Setting deleted", data=None)
