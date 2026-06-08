from cpkit import get_audit_actor
from cpkit.errors import ServiceError, raise_http_from_service_error
from fastapi import APIRouter, Depends

from ...models import DatabaseRoleTemplateConfig
from ...services.admin.cluster_options import ClusterOptionsService

router = APIRouter(prefix="/database_role_templates", tags=["admin"])


@router.get("/")
async def list_database_role_templates(
    service: ClusterOptionsService = Depends(ClusterOptionsService),
) -> list[DatabaseRoleTemplateConfig]:
    try:
        return service.list_database_role_templates()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_database_role_template(
    request: DatabaseRoleTemplateConfig,
    actor_id: str = Depends(get_audit_actor),
    service: ClusterOptionsService = Depends(ClusterOptionsService),
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
    service: ClusterOptionsService = Depends(ClusterOptionsService),
) -> None:
    try:
        service.delete_database_role_template(database_role_template, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
