"""Business logic for the cluster backups vertical."""

from pydantic import ValidationError

from ..models import BackupDetails, Cluster, ClusterBackupsSnapshot
from ..repos.postgres import cluster_backups
from . import cluster


def load_cluster_backups_snapshot(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> ClusterBackupsSnapshot | None:
    cluster = cluster.get_cluster_for_user(cluster_id, groups, is_admin)
    if cluster is None:
        return None

    return ClusterBackupsSnapshot(
        cluster=cluster,
        backup_paths=cluster_backups.list_backup_paths(_get_primary_dns_address(cluster)),
    )


def load_backup_details(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    backup_path: str,
) -> list[BackupDetails]:
    cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    return cluster_backups.list_backup_details(
        _get_primary_dns_address(cluster),
        backup_path,
    )


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
    cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)

    try:
        restore_request = cluster.validate_restore_request(
            name=cluster.cluster_id,
            backup_path=backup_path,
            restore_aost=restore_aost,
            restore_full_cluster=restore_full_cluster,
            object_type=object_type,
            object_name=object_name,
            backup_into=backup_into,
        )
    except ValidationError:
        raise

    return cluster.request_cluster_restore(
        cluster_id=cluster.cluster_id,
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
    cluster = cluster.get_cluster_for_user(cluster_id, groups, is_admin)
    if cluster is None:
        raise ValueError(f"Cluster {cluster_id} was not found")
    return cluster


def _get_primary_dns_address(cluster: Cluster) -> str:
    if not cluster.lbs_inventory:
        raise ValueError(f"Cluster {cluster.cluster_id} has no load balancer endpoint.")
    return cluster.lbs_inventory[0].dns_address
