"""Cluster API routes.

This router is the main cluster-facing HTTP surface: lifecycle commands,
dashboard snapshots, backups, database objects, database users, generated role
grants, and IdP group mappings. Business behavior belongs in services.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from cpkit import get_access_scope, get_audit_actor, require_readonly, require_user
from cpkit.errors import ServiceError, raise_http_from_service_error

from ..models import (
    ArtifactDownloadUrlResponse,
    BackupDetails,
    ClusterArtifactsSnapshot,
    ClusterBackupsSnapshot,
    ClusterCreateApiRequest,
    ClusterCreateOptionsResponse,
    ClusterDatabaseObject,
    ClusterDatabaseObjectDetails,
    ClusterDatabaseRoleGroupMapping,
    ClusterDatabaseRoleGroupsUpdateRequest,
    ClusterDatabaseRolesUpdateRequest,
    ClusterDialogOptionsResponse,
    ClusterJobsSnapshot,
    ClusterObjectRestoreApiRequest,
    ClusterOverview,
    ClusterPasswordUpdateRequest,
    ClusterPublic,
    ClusterRestoreApiRequest,
    ClusterScaleRequest,
    ClusterStatsResponse,
    ClusterUpgradeRequest,
    ClusterUsersSnapshot,
    CreateClusterDatabaseObjectRequest,
    DashboardSnapshot,
    DebugZipOptions,
    DebugZipRequest,
    ErrorResponse,
    JobID,
    NewDatabaseUserRequest,
)
from ..services.cluster import ClusterService
from ..services.cluster_backups import ClusterBackupsService
from ..services.cluster_jobs import ClusterJobsService
from ..services.cluster_users import ClusterUsersService
from ..services.dashboard import DashboardService

router = APIRouter(
    prefix="/clusters",
    tags=["clusters"],
)


@router.get("/")
async def list_clusters(
    claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(ClusterService),
) -> list[ClusterOverview]:
    """List clusters visible to the current CP principal."""
    groups, is_admin = get_access_scope(claims)
    try:
        return service.list_visible_clusters(groups, is_admin)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get("/stats", response_model=ClusterStatsResponse)
async def get_cluster_stats(
    claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(ClusterService),
) -> ClusterStatsResponse:
    """Return aggregate status counts for visible clusters."""
    groups, is_admin = get_access_scope(claims)
    try:
        return service.get_visible_cluster_stats(groups, is_admin)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get("/options", response_model=ClusterCreateOptionsResponse)
async def get_cluster_create_options(
    _claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(ClusterService),
) -> ClusterCreateOptionsResponse:
    """Return admin-configured options used by the create-cluster dialog."""
    try:
        return ClusterCreateOptionsResponse(**service.get_create_dialog_options())
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/", response_model=JobID)
async def create_cluster(
    request: ClusterCreateApiRequest,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(ClusterService),
) -> JobID:
    """Enqueue a create-cluster workflow and return the job id."""
    try:
        job_id = service.enqueue_cluster_creation(
            {"name": request.name},
            request.node_cpus,
            request.disk_size,
            request.node_count,
            request.regions,
            request.version,
            request.group,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}",
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def get_cluster(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(ClusterService),
) -> ClusterPublic:
    """Return one cluster when it is visible to the current CP principal."""
    groups, is_admin = get_access_scope(claims)
    try:
        cluster = service.get_cluster_for_user(cluster_id, groups, is_admin)
    except ServiceError as err:
        raise_http_from_service_error(err)
    if cluster is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return cluster


@router.delete(
    "/{cluster_id}",
    response_model=JobID,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def delete_cluster(
    cluster_id: str,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(ClusterService),
) -> JobID:
    """Enqueue a delete-cluster workflow for an existing managed cluster."""
    try:
        job_id = service.enqueue_cluster_deletion(cluster_id, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.post(
    "/{cluster_id}/debug-zip",
    response_model=JobID,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def create_cluster_debug_zip(
    cluster_id: str,
    request: DebugZipOptions | None = None,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(ClusterService),
) -> JobID:
    """Enqueue a CockroachDB debug zip collection job for an existing cluster."""
    payload = DebugZipRequest(
        cluster_id=cluster_id,
        **(request.model_dump() if request else {}),
    )
    try:
        job_id = service.enqueue_cluster_debug_zip(payload, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}/artifacts",
    response_model=ClusterArtifactsSnapshot,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def list_cluster_artifacts(
    cluster_id: str,
    kind: str | None = None,
    claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(ClusterService),
) -> ClusterArtifactsSnapshot:
    """Return artifact catalog entries for one visible cluster."""
    groups, is_admin = get_access_scope(claims)
    try:
        snapshot = service.list_cluster_artifacts(
            cluster_id,
            groups,
            is_admin,
            kind=kind,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return snapshot


@router.post(
    "/{cluster_id}/artifacts/{artifact_id}/download-url",
    response_model=ArtifactDownloadUrlResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Cluster artifact not found.",
        },
        409: {
            "model": ErrorResponse,
            "description": "Cluster artifact is not ready for download.",
        },
    },
)
async def create_cluster_artifact_download_url(
    cluster_id: str,
    artifact_id: str,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterService = Depends(ClusterService),
) -> ArtifactDownloadUrlResponse:
    """Create a presigned download URL for a ready cluster artifact."""
    groups, is_admin = get_access_scope(claims)
    try:
        return service.create_artifact_download_url(
            cluster_id,
            artifact_id,
            groups,
            is_admin,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post(
    "/{cluster_id}/healthcheck",
    response_model=JobID,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def healthcheck_cluster(
    cluster_id: str,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(ClusterService),
) -> JobID:
    """Enqueue the configured healthcheck playbook for an existing cluster."""
    try:
        job_id = service.enqueue_cluster_healthcheck(cluster_id, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}/options",
    response_model=ClusterDialogOptionsResponse,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def get_cluster_options(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(ClusterService),
) -> ClusterDialogOptionsResponse:
    """Return dialog options for changing an existing visible cluster."""
    groups, is_admin = get_access_scope(claims)
    try:
        cluster = service.get_cluster_for_user(cluster_id, groups, is_admin)
        if cluster is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cluster '{cluster_id}' was not found.",
            )
        return ClusterDialogOptionsResponse(
            **service.get_cluster_dialog_options(cluster)
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/scale", response_model=JobID)
async def scale_cluster(
    request: ClusterScaleRequest,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(ClusterService),
) -> JobID:
    """Enqueue a scale workflow for node count, CPU, disk, or region changes."""
    try:
        job_id = service.enqueue_cluster_scale(
            request,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.post("/upgrade", response_model=JobID)
async def upgrade_cluster(
    request: ClusterUpgradeRequest,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(ClusterService),
) -> JobID:
    """Enqueue a cluster version upgrade workflow."""
    try:
        job_id = service.enqueue_cluster_upgrade(
            request,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}/jobs",
    response_model=ClusterJobsSnapshot,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def get_cluster_jobs(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterJobsService = Depends(ClusterJobsService),
) -> ClusterJobsSnapshot:
    """Return jobs linked to one visible cluster."""
    groups, is_admin = get_access_scope(claims)
    try:
        snapshot = service.load_cluster_jobs_snapshot(cluster_id, groups, is_admin)
    except ServiceError as err:
        raise_http_from_service_error(err)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return snapshot


@router.get(
    "/{cluster_id}/backups",
    response_model=ClusterBackupsSnapshot,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def get_cluster_backups(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterBackupsService = Depends(ClusterBackupsService),
) -> ClusterBackupsSnapshot:
    """Return backup path options for one visible cluster."""
    groups, is_admin = get_access_scope(claims)
    try:
        snapshot = service.load_cluster_backups_snapshot(cluster_id, groups, is_admin)
    except ServiceError as err:
        raise_http_from_service_error(err)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return snapshot


@router.get("/{cluster_id}/backups/details")
async def get_cluster_backup_details(
    cluster_id: str,
    backup_path: str,
    claims: dict = Depends(require_readonly),
    service: ClusterBackupsService = Depends(ClusterBackupsService),
) -> list[BackupDetails]:
    """Return the object contents for one backup path."""
    groups, is_admin = get_access_scope(claims)
    try:
        return service.load_backup_details(cluster_id, groups, is_admin, backup_path)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/{cluster_id}/backups/restore", response_model=JobID)
async def restore_cluster(
    cluster_id: str,
    request: ClusterRestoreApiRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterBackupsService = Depends(ClusterBackupsService),
) -> JobID:
    """Enqueue a restore workflow from a selected cluster backup path."""
    groups, is_admin = get_access_scope(claims)
    try:
        job_id = service.enqueue_cluster_restore(
            cluster_id,
            groups,
            is_admin,
            request.backup_path,
            request.restore_aost,
            request.restore_full_cluster,
            request.object_type,
            request.object_name,
            request.backup_into,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.post("/{cluster_id}/restore/objects", response_model=JobID)
async def restore_cluster_object(
    cluster_id: str,
    request: ClusterObjectRestoreApiRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterBackupsService = Depends(ClusterBackupsService),
) -> JobID:
    """Enqueue a restore workflow for one database or table object."""
    groups, is_admin = get_access_scope(claims)
    try:
        job_id = service.enqueue_object_restore(
            cluster_id,
            groups,
            is_admin,
            request.backup_path,
            request.restore_aost,
            request.object_type,
            request.object_name,
            request.into_db,
            request.new_db_name,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}/database-objects",
    response_model=list[ClusterDatabaseObjectDetails],
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def list_cluster_database_objects(
    cluster_id: str,
    claims: dict = Depends(require_user),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> list[ClusterDatabaseObjectDetails]:
    """List database cards and their generated roles; mappings are read separately."""
    groups, is_admin = get_access_scope(claims)
    try:
        database_objects = service.list_database_objects(cluster_id, groups, is_admin)
    except ServiceError as err:
        raise_http_from_service_error(err)
    if database_objects is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return database_objects


@router.post(
    "/{cluster_id}/database-objects",
    response_model=ClusterDatabaseObject,
)
async def create_cluster_database_object(
    cluster_id: str,
    request: CreateClusterDatabaseObjectRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> ClusterDatabaseObject:
    """Create a database in the cluster and materialize default generated roles."""
    groups, is_admin = get_access_scope(claims)
    try:
        return service.create_database_object(
            cluster_id,
            groups,
            is_admin,
            request.database_name,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get(
    "/{cluster_id}/database-objects/{database_name}",
    response_model=ClusterDatabaseObject,
    responses={
        404: {"model": ErrorResponse, "description": "Database object not found."}
    },
)
async def get_cluster_database_object(
    cluster_id: str,
    database_name: str,
    claims: dict = Depends(require_user),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> ClusterDatabaseObject:
    """Return one managed database object recorded by CP."""
    groups, is_admin = get_access_scope(claims)
    try:
        database_object = service.get_database_object(
            cluster_id,
            groups,
            is_admin,
            database_name,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    if database_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database object '{database_name}' was not found.",
        )
    return database_object


@router.delete("/{cluster_id}/database-objects/{database_name}")
async def delete_cluster_database_object(
    cluster_id: str,
    database_name: str,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> None:
    """Drop a managed database object and remove its generated roles from CP."""
    groups, is_admin = get_access_scope(claims)
    try:
        service.delete_database_object(
            cluster_id,
            groups,
            is_admin,
            database_name,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get(
    "/{cluster_id}/database-role-group-mappings",
    response_model=list[ClusterDatabaseRoleGroupMapping],
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def list_cluster_database_role_group_mappings(
    cluster_id: str,
    claims: dict = Depends(require_user),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> list[ClusterDatabaseRoleGroupMapping]:
    """List the stored IdP group to generated database role mappings."""
    groups, is_admin = get_access_scope(claims)
    try:
        mappings = service.list_database_role_group_mappings(
            cluster_id,
            groups,
            is_admin,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    if mappings is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return mappings


@router.put(
    "/{cluster_id}/database-role-group-mappings/{database_role}",
    response_model=list[ClusterDatabaseRoleGroupMapping],
)
async def update_cluster_database_role_group_mappings(
    cluster_id: str,
    database_role: str,
    request: ClusterDatabaseRoleGroupsUpdateRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> list[ClusterDatabaseRoleGroupMapping]:
    """Replace all IdP groups mapped to one generated database role."""
    groups, is_admin = get_access_scope(claims)
    try:
        return service.update_database_role_group_mappings(
            cluster_id,
            groups,
            is_admin,
            database_role,
            request.groups,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get(
    "/{cluster_id}/users",
    response_model=ClusterUsersSnapshot,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def get_cluster_users(
    cluster_id: str,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> ClusterUsersSnapshot:
    """Return database users plus role options for User Management."""
    groups, is_admin = get_access_scope(claims)
    try:
        snapshot = service.load_cluster_users_snapshot(
            cluster_id,
            groups,
            is_admin,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return snapshot


@router.post("/{cluster_id}/users")
async def create_cluster_user(
    cluster_id: str,
    request: NewDatabaseUserRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> None:
    """Create a database user and optionally grant generated database roles."""
    groups, is_admin = get_access_scope(claims)
    try:
        service.create_database_user(
            cluster_id,
            groups,
            is_admin,
            request.username,
            request.password,
            request.database_roles,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{cluster_id}/users/{username}")
async def delete_cluster_user(
    cluster_id: str,
    username: str,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> None:
    """Drop a database user from the managed cluster."""
    groups, is_admin = get_access_scope(claims)
    try:
        service.delete_database_user(
            cluster_id,
            groups,
            is_admin,
            username,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/{cluster_id}/users/{username}/grant-database-roles")
async def grant_cluster_user_database_roles(
    cluster_id: str,
    username: str,
    request: ClusterDatabaseRolesUpdateRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> None:
    """Grant one or more generated database roles directly to a database user."""
    groups, is_admin = get_access_scope(claims)
    try:
        service.grant_database_user_roles(
            cluster_id,
            groups,
            is_admin,
            username,
            request.database_roles,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/{cluster_id}/users/{username}/revoke-database-roles")
async def revoke_cluster_user_database_roles(
    cluster_id: str,
    username: str,
    request: ClusterDatabaseRolesUpdateRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> None:
    """Revoke one or more generated database roles directly from a database user."""
    groups, is_admin = get_access_scope(claims)
    try:
        service.revoke_database_user_roles(
            cluster_id,
            groups,
            is_admin,
            username,
            request.database_roles,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/{cluster_id}/users/{username}/password")
async def update_cluster_user_password(
    cluster_id: str,
    username: str,
    request: ClusterPasswordUpdateRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(ClusterUsersService),
) -> None:
    """Update the password for a database user in the managed cluster."""
    groups, is_admin = get_access_scope(claims)
    try:
        service.update_database_user_password(
            cluster_id,
            groups,
            is_admin,
            username,
            request.password,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get(
    "/{cluster_id}/dashboard",
    response_model=DashboardSnapshot,
    responses={404: {"model": ErrorResponse, "description": "Cluster not found."}},
)
async def get_cluster_dashboard(
    cluster_id: str,
    start: int = 0,
    end: int = 0,
    interval_secs: int = 10,
    claims: dict = Depends(require_readonly),
    service: DashboardService = Depends(DashboardService),
) -> DashboardSnapshot:
    """Return metadata and metrics for the Cluster Dashboard page."""
    groups, is_admin = get_access_scope(claims)
    try:
        snapshot = service.load_dashboard_snapshot(
            cluster_id,
            groups,
            is_admin,
            start,
            end,
            interval_secs,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return snapshot
