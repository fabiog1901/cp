from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.exceptions import RequestErrorModel

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
    ClusterDeleteApiRequest,
    ClusterDialogOptionsResponse,
    ClusterJobsSnapshot,
    ClusterOverview,
    ClusterPasswordUpdateRequest,
    ClusterRestoreApiRequest,
    ClusterRoleRevokeRequest,
    ClusterScaleRequest,
    ClusterUpgradeApiRequest,
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
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterService = Depends(get_cluster_service),
) -> list[ClusterOverview]:
    try:
        return service.list_visible_clusters(groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.get("/options", response_model=ClusterCreateOptionsResponse)
async def get_cluster_create_options(
    service: ClusterService = Depends(get_cluster_service),
) -> ClusterCreateOptionsResponse:
    try:
        return ClusterCreateOptionsResponse(**service.get_create_dialog_options())
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/", response_model=JobID)
async def create_cluster(
    request: ClusterCreateApiRequest,
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
            request.requested_by,
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
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterService = Depends(get_cluster_service),
) -> Cluster:
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
    request: ClusterDeleteApiRequest,
    service: ClusterService = Depends(get_cluster_service),
) -> JobID:
    try:
        job_id = service.request_cluster_deletion(cluster_id, request.requested_by)
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
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterService = Depends(get_cluster_service),
) -> ClusterDialogOptionsResponse:
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


@router.post("/{cluster_id}/scale", response_model=JobID)
async def scale_cluster(
    cluster_id: str,
    request: ClusterScaleRequest,
    requested_by: str,
    service: ClusterService = Depends(get_cluster_service),
) -> JobID:
    try:
        job_id = service.request_cluster_scale(
            cluster_id,
            request.node_cpus,
            request.disk_size,
            request.node_count,
            request.regions,
            requested_by,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)
    return JobID(job_id=job_id)


@router.post("/{cluster_id}/upgrade", response_model=JobID)
async def upgrade_cluster(
    cluster_id: str,
    request: ClusterUpgradeApiRequest,
    service: ClusterService = Depends(get_cluster_service),
) -> JobID:
    try:
        job_id = service.request_cluster_upgrade(
            cluster_id,
            request.version,
            request.auto_finalize,
            request.requested_by,
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
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterJobsService = Depends(get_cluster_jobs_service),
) -> ClusterJobsSnapshot:
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
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterBackupsService = Depends(get_cluster_backups_service),
) -> ClusterBackupsSnapshot:
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
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterBackupsService = Depends(get_cluster_backups_service),
) -> list[BackupDetails]:
    try:
        return service.load_backup_details(cluster_id, groups, is_admin, backup_path)
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/{cluster_id}/backups/restore", response_model=JobID)
async def restore_cluster(
    cluster_id: str,
    request: ClusterRestoreApiRequest,
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterBackupsService = Depends(get_cluster_backups_service),
) -> JobID:
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
            request.requested_by,
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
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> ClusterUsersSnapshot:
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
    requested_by: str,
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> None:
    try:
        service.create_database_user(
            cluster_id,
            groups,
            is_admin,
            request.username,
            request.password,
            requested_by,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.delete("/{cluster_id}/users/{username}")
async def delete_cluster_user(
    cluster_id: str,
    username: str,
    requested_by: str,
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> None:
    try:
        service.remove_database_user(
            cluster_id,
            groups,
            is_admin,
            username,
            requested_by,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/{cluster_id}/users/{username}/revoke-role")
async def revoke_cluster_user_role(
    cluster_id: str,
    username: str,
    request: ClusterRoleRevokeRequest,
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> None:
    try:
        service.revoke_database_user_role(
            cluster_id,
            groups,
            is_admin,
            username,
            request.role,
            request.requested_by,
        )
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/{cluster_id}/users/{username}/password")
async def update_cluster_user_password(
    cluster_id: str,
    username: str,
    request: ClusterPasswordUpdateRequest,
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: ClusterUsersService = Depends(get_cluster_users_service),
) -> None:
    try:
        service.update_database_user_password(
            cluster_id,
            groups,
            is_admin,
            username,
            request.password,
            request.requested_by,
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
    groups: list[str] = Query(default_factory=list),
    is_admin: bool = False,
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSnapshot:
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
