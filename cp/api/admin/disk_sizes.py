from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_cluster_options_service
from ...models import DiskSizeOption
from ...services.admin.cluster_options import ClusterOptionsService
from ...services.errors import ServiceError
from .common import raise_http_from_service_error

router = APIRouter(prefix="/disk_sizes", tags=["admin"])


@router.get("/")
async def list_disk_sizes(
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> list[DiskSizeOption]:
    try:
        return service.list_disk_sizes()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_disk_size(
    request: DiskSizeOption,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> DiskSizeOption:
    try:
        return service.create_disk_size(request.size_gb, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{size_gb}")
async def delete_disk_size(
    size_gb: int,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> None:
    try:
        service.delete_disk_size(size_gb, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
