from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_settings_service
from ...models import SettingRecord, SettingUpdateRequest
from ...services.errors import ServiceError
from ...services.admin.settings import SettingsService
from .common import raise_http_from_service_error

router = APIRouter(prefix="/settings", tags=["admin"])


@router.get("/")
async def list_settings(
    service: SettingsService = Depends(get_settings_service),
) -> list[SettingRecord]:
    try:
        return service.list_settings()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get("/{setting_id}")
async def get_setting(
    setting_id: str,
    service: SettingsService = Depends(get_settings_service),
) -> str:
    try:
        return service.get_setting(setting_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.patch("/{setting_id}")
async def update_setting(
    setting_id: str,
    request: SettingUpdateRequest,
    actor_id: str = Depends(get_audit_actor),
    service: SettingsService = Depends(get_settings_service),
) -> None:
    try:
        service.update_setting(setting_id, request.value, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.put("/{setting_id}/reset")
async def reset_setting(
    setting_id: str,
    actor_id: str = Depends(get_audit_actor),
    service: SettingsService = Depends(get_settings_service),
) -> None:
    try:
        service.reset_setting(setting_id, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
