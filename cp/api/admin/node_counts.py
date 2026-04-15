from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_cluster_options_service
from ...models import NodeCountOption
from ...services.admin.cluster_options import ClusterOptionsService
from ...services.errors import ServiceError
from .common import raise_http_from_service_error

router = APIRouter(prefix="/node_counts", tags=["admin"])


@router.get("/")
async def list_node_counts(
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> list[NodeCountOption]:
    try:
        return service.list_node_counts()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_node_count(
    request: NodeCountOption,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> NodeCountOption:
    try:
        return service.create_node_count(request.node_count, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{node_count}")
async def delete_node_count(
    node_count: int,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> None:
    try:
        service.delete_node_count(node_count, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
