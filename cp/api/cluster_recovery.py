"""Cluster recovery API routes.

This router exposes backup catalog views and restore entry points used by the
cluster recovery page. Restore orchestration is delegated to BackupCatalogService.
"""

from fastapi import APIRouter, Depends, Query

from cpkit import get_access_scope, get_audit_actor, require_readonly, require_user
from cpkit.errors import ServiceError, raise_http_from_service_error

from ..models import BackupCatalogSnapshot, ClusterRecoveryRestoreApiRequest, JobID
from ..services.backup_catalog import BackupCatalogService

router = APIRouter(
    prefix="/cluster-recovery",
    tags=["cluster-recovery"],
)


@router.get("/backups", response_model=BackupCatalogSnapshot)
async def list_recovery_backups(
    full_cluster_only: bool = Query(default=True),
    claims: dict = Depends(require_readonly),
    service: BackupCatalogService = Depends(BackupCatalogService),
) -> BackupCatalogSnapshot:
    groups, is_admin = get_access_scope(claims)
    try:
        backups = service.list_backups(
            groups,
            is_admin,
            full_cluster_only=full_cluster_only,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    return BackupCatalogSnapshot(backups=backups)


@router.post("/backups/sync")
async def sync_recovery_backups(
    cluster_id: str | None = Query(default=None),
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: BackupCatalogService = Depends(BackupCatalogService),
) -> dict[str, str]:
    groups, is_admin = get_access_scope(claims)
    try:
        service.enqueue_sync(actor_id, groups, is_admin, cluster_id=cluster_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
    return {"status": "queued"}


@router.post("/restores", response_model=JobID)
async def restore_full_cluster(
    request: ClusterRecoveryRestoreApiRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: BackupCatalogService = Depends(BackupCatalogService),
) -> JobID:
    groups, is_admin = get_access_scope(claims)
    try:
        job_id = service.enqueue_full_cluster_restore(
            request,
            groups,
            is_admin,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)
