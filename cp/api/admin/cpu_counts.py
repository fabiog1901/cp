from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_cluster_options_service
from ...models import CpuCountOption
from ...services.admin.cluster_options import ClusterOptionsService
from ...services.errors import ServiceError
from .common import raise_http_from_service_error

router = APIRouter(prefix="/cpu_counts", tags=["admin"])


@router.get("/")
async def list_cpu_counts(
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> list[CpuCountOption]:
    try:
        return service.list_cpu_counts()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_cpu_count(
    request: CpuCountOption,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> CpuCountOption:
    try:
        return service.create_cpu_count(request.cpu_count, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{cpu_count}")
async def delete_cpu_count(
    cpu_count: int,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> None:
    try:
        service.delete_cpu_count(cpu_count, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
