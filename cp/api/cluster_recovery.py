from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth import get_access_scope, get_audit_actor, require_readonly, require_user
from ..infra import get_backup_catalog_service
from ..models import BackupCatalogSnapshot
from ..services.backup_catalog import BackupCatalogService
from ..services.errors import (
    ServiceAuthorizationError,
    ServiceError,
    ServiceNotFoundError,
    ServiceUnavailableError,
    ServiceValidationError,
)

router = APIRouter(
    prefix="/cluster-recovery",
    tags=["cluster-recovery"],
)


def _raise_http_from_service_error(err: ServiceError) -> None:
    if isinstance(err, ServiceNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.user_message,
        )
    if isinstance(err, ServiceValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.user_message,
        )
    if isinstance(err, ServiceAuthorizationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err.user_message,
        )
    if isinstance(err, ServiceUnavailableError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=err.user_message,
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=err.user_message,
    )


@router.get("/backups", response_model=BackupCatalogSnapshot)
async def list_recovery_backups(
    full_cluster_only: bool = Query(default=True),
    claims: dict = Depends(require_readonly),
    service: BackupCatalogService = Depends(get_backup_catalog_service),
) -> BackupCatalogSnapshot:
    groups, is_admin = get_access_scope(claims)
    try:
        backups = service.list_backups(
            groups,
            is_admin,
            full_cluster_only=full_cluster_only,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)
    return BackupCatalogSnapshot(backups=backups)


@router.post("/backups/sync")
async def sync_recovery_backups(
    cluster_id: str | None = Query(default=None),
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: BackupCatalogService = Depends(get_backup_catalog_service),
) -> dict[str, str]:
    groups, is_admin = get_access_scope(claims)
    try:
        service.enqueue_sync(actor_id, groups, is_admin, cluster_id=cluster_id)
    except ServiceError as err:
        _raise_http_from_service_error(err)
    return {"status": "queued"}
