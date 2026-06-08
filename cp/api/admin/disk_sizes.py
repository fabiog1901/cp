from cpkit import get_audit_actor
from cpkit.errors import ServiceError, raise_http_from_service_error
from fastapi import APIRouter, Depends

from ...models import DiskSizeOption
from ...services.admin.cluster_options import ClusterOptionsService

router = APIRouter(prefix="/disk_sizes", tags=["admin"])


@router.get("/")
async def list_disk_sizes(
    service: ClusterOptionsService = Depends(ClusterOptionsService),
) -> list[DiskSizeOption]:
    try:
        return service.list_disk_sizes()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_disk_size(
    request: DiskSizeOption,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(ClusterOptionsService),
) -> DiskSizeOption:
    try:
        return service.create_disk_size(request.size_gb, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{size_gb}")
async def delete_disk_size(
    size_gb: int,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(ClusterOptionsService),
) -> None:
    try:
        service.delete_disk_size(size_gb, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
