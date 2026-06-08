from fastapi import APIRouter, Depends

from cpkit import get_audit_actor
from cpkit.errors import ServiceError, raise_http_from_service_error

from ...models import CpuCountOption
from ...services.admin.cluster_options import ClusterOptionsService

router = APIRouter(prefix="/cpu_counts", tags=["admin"])


@router.get("/")
async def list_cpu_counts(
    service: ClusterOptionsService = Depends(ClusterOptionsService),
) -> list[CpuCountOption]:
    try:
        return service.list_cpu_counts()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_cpu_count(
    request: CpuCountOption,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(ClusterOptionsService),
) -> CpuCountOption:
    try:
        return service.create_cpu_count(request.cpu_count, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{cpu_count}")
async def delete_cpu_count(
    cpu_count: int,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(ClusterOptionsService),
) -> None:
    try:
        service.delete_cpu_count(cpu_count, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
