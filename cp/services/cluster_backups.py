"""Business logic for the cluster backups vertical."""

from ..infra.errors import RepositoryError
from ..models import BackupDetails, Cluster, ClusterBackupsSnapshot
from ..repos.postgres.cluster_backups_repo import ClusterBackupsRepo
from .cluster import ClusterService
from .errors import ServiceNotFoundError, ServiceValidationError, from_repository_error


def load_cluster_backups_snapshot(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> ClusterBackupsSnapshot | None:
    selected_cluster = ClusterService.get_cluster_for_user(cluster_id, groups, is_admin)
    if selected_cluster is None:
        return None

    try:
        return ClusterBackupsSnapshot(
            cluster=selected_cluster,
            backup_paths=ClusterBackupsRepo.list_backup_paths(
                _get_primary_dns_address(selected_cluster)
            ),
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster backups are temporarily unavailable.",
            fallback_message=f"Unable to load backups for cluster '{cluster_id}'.",
        ) from err


def load_backup_details(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    backup_path: str,
) -> list[BackupDetails]:
    selected_cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    try:
        return ClusterBackupsRepo.list_backup_details(
            _get_primary_dns_address(selected_cluster),
            backup_path,
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Backup details are temporarily unavailable.",
            fallback_message=f"Unable to load backup details for cluster '{cluster_id}'.",
        ) from err


def request_cluster_restore(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    backup_path: str,
    restore_aost: str | None,
    restore_full_cluster: bool,
    object_type: str | None,
    object_name: str | None,
    backup_into: str | None,
    requested_by: str,
) -> int:
    selected_cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    restore_request = ClusterService.validate_restore_request(
        name=selected_cluster.cluster_id,
        backup_path=backup_path,
        restore_aost=restore_aost,
        restore_full_cluster=restore_full_cluster,
        object_type=object_type,
        object_name=object_name,
        backup_into=backup_into,
    )

    return ClusterService.request_cluster_restore(
        cluster_id=selected_cluster.cluster_id,
        backup_path=restore_request["backup_path"],
        restore_aost=restore_request["restore_aost"],
        restore_full_cluster=restore_request["restore_full_cluster"],
        object_type=restore_request["object_type"],
        object_name=restore_request["object_name"],
        backup_into=restore_request["backup_into"],
        requested_by=requested_by,
    )


def _get_cluster_or_raise(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> Cluster:
    selected_cluster = ClusterService.get_cluster_for_user(cluster_id, groups, is_admin)
    if selected_cluster is None:
        raise ServiceNotFoundError(f"Cluster '{cluster_id}' was not found.")
    return selected_cluster


def _get_primary_dns_address(cluster: Cluster) -> str:
    if not cluster.lbs_inventory:
        raise ServiceValidationError(
            f"Cluster '{cluster.cluster_id}' has no load balancer endpoint."
        )
    return cluster.lbs_inventory[0].dns_address
