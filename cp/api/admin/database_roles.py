from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_cluster_options_service
from ...models import DatabaseRoleConfig
from ...services.admin.cluster_options import ClusterOptionsService
from ...services.errors import ServiceError
from .common import raise_http_from_service_error

router = APIRouter(prefix="/database_roles", tags=["admin"])


@router.get("/")
async def list_database_roles(
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> list[DatabaseRoleConfig]:
    try:
        return service.list_database_roles()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_database_role(
    request: DatabaseRoleConfig,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> DatabaseRoleConfig:
    try:
        return service.create_database_role(
            request.role_name,
            request.sql_statement,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{role}")
async def delete_database_role(
    role: str,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> None:
    try:
        service.delete_database_role(role, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
