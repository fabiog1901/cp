from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_cluster_options_service
from ...models import DatabaseRoleTemplateConfig
from ...services.admin.cluster_options import ClusterOptionsService
from ...services.errors import ServiceError
from .common import raise_http_from_service_error

router = APIRouter(prefix="/database_role_templates", tags=["admin"])


@router.get("/")
async def list_database_role_templates(
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> list[DatabaseRoleTemplateConfig]:
    try:
        return service.list_database_role_templates()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_database_role_template(
    request: DatabaseRoleTemplateConfig,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> DatabaseRoleTemplateConfig:
    try:
        return service.create_database_role_template(
            request.database_role_template,
            request.scope_type,
            request.sql_statement,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{database_role_template}")
async def delete_database_role_template(
    database_role_template: str,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(get_cluster_options_service),
) -> None:
    try:
        service.delete_database_role_template(database_role_template, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
