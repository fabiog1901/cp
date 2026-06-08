from cpkit import get_audit_actor
from cpkit.errors import ServiceError, raise_http_from_service_error
from fastapi import APIRouter, Depends

from ...models import Version
from ...services.admin.versions import VersionsService

router = APIRouter(prefix="/versions", tags=["admin"])


@router.get("/")
async def list_versions(
    service: VersionsService = Depends(VersionsService),
) -> list[Version]:
    try:
        return service.list_versions()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_version(
    request: Version,
    actor_id: str = Depends(get_audit_actor),
    service: VersionsService = Depends(VersionsService),
) -> Version:
    try:
        return service.create_version(request.version, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{version}")
async def delete_version(
    version: str,
    actor_id: str = Depends(get_audit_actor),
    service: VersionsService = Depends(VersionsService),
) -> None:
    try:
        service.delete_version(version, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
