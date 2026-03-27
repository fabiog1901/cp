from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import RequestErrorModel

from ..auth import get_access_scope, get_audit_actor, require_readonly, require_user
from ..infra import (
    get_cluster_backups_service,
    get_cluster_jobs_service,
    get_cluster_service,
    get_cluster_users_service,
    get_dashboard_service,
)
from ..models import (
    BackupDetails,
    Cluster,
    ClusterBackupsSnapshot,
    ClusterCreateApiRequest,
    ClusterCreateOptionsResponse,
    ClusterDialogOptionsResponse,
    ClusterJobsSnapshot,
    ClusterOverview,
    ClusterPasswordUpdateRequest,
    ClusterRestoreApiRequest,
    ClusterRoleRevokeRequest,
    ClusterScaleRequest,
    ClusterUpgradeRequest,
    ClusterUsersSnapshot,
    DashboardSnapshot,
    JobID,
    NewDatabaseUserRequest,
)
from ..services.cluster import ClusterService
from ..services.cluster_backups import ClusterBackupsService
from ..services.cluster_jobs import ClusterJobsService
from ..services.cluster_users import ClusterUsersService
from ..services.dashboard import DashboardService
from ..services.errors import (
    ServiceAuthorizationError,
    ServiceError,
    ServiceNotFoundError,
    ServiceUnavailableError,
    ServiceValidationError,
)

router = APIRouter(
    prefix="/clusters",
    tags=["clusters"],
)


def _raise_http_from_service_error(err: ServiceError) -> None:
    if isinstance(err, ServiceNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=err.user_message
        )
    if isinstance(err, ServiceValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=err.user_message
        )
    if isinstance(err, ServiceAuthorizationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=err.user_message
        )
    if isinstance(err, ServiceUnavailableError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=err.user_message
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err.user_message
    )


@router.get("/")
async def list_clusters(
    claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(get_cluster_service),
) -> list[ClusterOverview]:
    groups, is_admin = get_access_scope(claims)
    try:
        return service.list_visible_clusters(groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.get("/options", response_model=ClusterCreateOptionsResponse)
async def get_cluster_create_options(
    _claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(get_cluster_service),
) -> ClusterCreateOptionsResponse:
    try:
        return ClusterCreateOptionsResponse(**service.get_create_dialog_options())
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/", response_model=JobID)
async def create_cluster(
    request: ClusterCreateApiRequest,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(get_cluster_service),
) -> JobID:
    try:
        job_id = service.request_cluster_creation(
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
        _raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}",
    responses={404: {"model": RequestErrorModel, "description": "Cluster not found."}},
)
async def get_cluster(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(get_cluster_service),
) -> Cluster:
    groups, is_admin = get_access_scope(claims)
    try:
        cluster = service.get_cluster_for_user(cluster_id, groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)
    if cluster is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return cluster


@router.delete(
    "/{cluster_id}",
    response_model=JobID,
    responses={404: {"model": RequestErrorModel, "description": "Cluster not found."}},
)
async def delete_cluster(
    cluster_id: str,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(get_cluster_service),
) -> JobID:
    try:
        job_id = service.request_cluster_deletion(cluster_id, actor_id)
    except ServiceError as err:
        _raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}/options",
    response_model=ClusterDialogOptionsResponse,
    responses={404: {"model": RequestErrorModel, "description": "Cluster not found."}},
)
async def get_cluster_options(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterService = Depends(get_cluster_service),
) -> ClusterDialogOptionsResponse:
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
        _raise_http_from_service_error(err)


@router.post("/scale", response_model=JobID)
async def scale_cluster(
    request: ClusterScaleRequest,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(get_cluster_service),
) -> JobID:
    try:
        job_id = service.request_cluster_scale(
            request,
            actor_id,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.post("/upgrade", response_model=JobID)
async def upgrade_cluster(
    request: ClusterUpgradeRequest,
    actor_id: str = Depends(get_audit_actor),
    _claims: dict = Depends(require_user),
    service: ClusterService = Depends(get_cluster_service),
) -> JobID:
    try:
        job_id = service.request_cluster_upgrade(
            request,
            actor_id,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}/jobs",
    response_model=ClusterJobsSnapshot,
    responses={404: {"model": RequestErrorModel, "description": "Cluster not found."}},
)
async def get_cluster_jobs(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterJobsService = Depends(get_cluster_jobs_service),
) -> ClusterJobsSnapshot:
    groups, is_admin = get_access_scope(claims)
    try:
        snapshot = service.load_cluster_jobs_snapshot(cluster_id, groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return snapshot


@router.get(
    "/{cluster_id}/backups",
    response_model=ClusterBackupsSnapshot,
    responses={404: {"model": RequestErrorModel, "description": "Cluster not found."}},
)
async def get_cluster_backups(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterBackupsService = Depends(get_cluster_backups_service),
) -> ClusterBackupsSnapshot:
    groups, is_admin = get_access_scope(claims)
    try:
        snapshot = service.load_cluster_backups_snapshot(cluster_id, groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)
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
    service: ClusterBackupsService = Depends(get_cluster_backups_service),
) -> list[BackupDetails]:
    groups, is_admin = get_access_scope(claims)
    try:
        return service.load_backup_details(cluster_id, groups, is_admin, backup_path)
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/{cluster_id}/backups/restore", response_model=JobID)
async def restore_cluster(
    cluster_id: str,
    request: ClusterRestoreApiRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterBackupsService = Depends(get_cluster_backups_service),
) -> JobID:
    groups, is_admin = get_access_scope(claims)
    try:
        job_id = service.request_cluster_restore(
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
        _raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.get(
    "/{cluster_id}/users",
    response_model=ClusterUsersSnapshot,
    responses={404: {"model": RequestErrorModel, "description": "Cluster not found."}},
)
async def get_cluster_users(
    cluster_id: str,
    claims: dict = Depends(require_readonly),
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> ClusterUsersSnapshot:
    groups, is_admin = get_access_scope(claims)
    try:
        snapshot = service.load_cluster_users_snapshot(cluster_id, groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)
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
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> None:
    groups, is_admin = get_access_scope(claims)
    try:
        service.create_database_user(
            cluster_id,
            groups,
            is_admin,
            request.username,
            request.password,
            actor_id,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.delete("/{cluster_id}/users/{username}")
async def delete_cluster_user(
    cluster_id: str,
    username: str,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> None:
    groups, is_admin = get_access_scope(claims)
    try:
        service.remove_database_user(
            cluster_id,
            groups,
            is_admin,
            username,
            actor_id,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/{cluster_id}/users/{username}/revoke-role")
async def revoke_cluster_user_role(
    cluster_id: str,
    username: str,
    request: ClusterRoleRevokeRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> None:
    groups, is_admin = get_access_scope(claims)
    try:
        service.revoke_database_user_role(
            cluster_id,
            groups,
            is_admin,
            username,
            request.role,
            actor_id,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/{cluster_id}/users/{username}/password")
async def update_cluster_user_password(
    cluster_id: str,
    username: str,
    request: ClusterPasswordUpdateRequest,
    claims: dict = Depends(require_user),
    actor_id: str = Depends(get_audit_actor),
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> None:
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
        _raise_http_from_service_error(err)


@router.get(
    "/{cluster_id}/dashboard",
    response_model=DashboardSnapshot,
    responses={404: {"model": RequestErrorModel, "description": "Cluster not found."}},
)
async def get_cluster_dashboard(
    cluster_id: str,
    start: int = 0,
    end: int = 0,
    interval_secs: int = 10,
    claims: dict = Depends(require_readonly),
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSnapshot:
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
        _raise_http_from_service_error(err)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster '{cluster_id}' was not found.",
        )
    return snapshot
