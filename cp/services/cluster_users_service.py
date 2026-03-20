"""Business logic for the cluster users vertical."""

from ..models import Cluster, ClusterUsersSnapshot, EventType, NewDatabaseUserRequest
from ..repos.postgres import cluster_users_repo
from . import app_service, cluster_service


def load_cluster_users_snapshot(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> ClusterUsersSnapshot | None:
    cluster = cluster_service.get_cluster_for_user(cluster_id, groups, is_admin)
    if cluster is None:
        return None

    return ClusterUsersSnapshot(
        cluster=cluster,
        database_users=cluster_users_repo.list_database_users(
            _get_primary_dns_address(cluster)
        ),
    )


def create_database_user(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    username: str,
    password: str,
    requested_by: str,
) -> None:
    cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    request = NewDatabaseUserRequest(username=username, password=password)
    cluster_users_repo.create_database_user(
        _get_primary_dns_address(cluster),
        request.username,
        request.password,
    )
    app_service.insert_event_log(
        requested_by,
        EventType.DB_USER_ADD,
        {"cluster_id": cluster.cluster_id, "db_user": request.username},
    )


def remove_database_user(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    username: str,
    requested_by: str,
) -> None:
    cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    cluster_users_repo.remove_database_user(
        _get_primary_dns_address(cluster),
        username,
    )
    app_service.insert_event_log(
        requested_by,
        EventType.DB_USER_REMOVE,
        {"cluster_id": cluster.cluster_id, "db_user": username},
    )


def revoke_database_user_role(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    username: str,
    role: str,
    requested_by: str,
) -> None:
    cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    cluster_users_repo.revoke_database_user_role(
        _get_primary_dns_address(cluster),
        username,
        role,
    )
    app_service.insert_event_log(
        requested_by,
        EventType.DB_USER_REMOVE_ROLE,
        {"cluster_id": cluster.cluster_id, "db_user": username, "role": role},
    )


def update_database_user_password(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    username: str,
    password: str,
    requested_by: str,
) -> None:
    if not password:
        raise ValueError("Password is required.")

    cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    cluster_users_repo.update_database_user_password(
        _get_primary_dns_address(cluster),
        username,
        password,
    )
    app_service.insert_event_log(
        requested_by,
        EventType.DB_USER_UPDATE,
        {"cluster_id": cluster.cluster_id, "db_user": username},
    )


def _get_cluster_or_raise(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> Cluster:
    cluster = cluster_service.get_cluster_for_user(cluster_id, groups, is_admin)
    if cluster is None:
        raise ValueError(f"Cluster {cluster_id} was not found")
    return cluster


def _get_primary_dns_address(cluster: Cluster) -> str:
    if not cluster.lbs_inventory:
        raise ValueError(f"Cluster {cluster.cluster_id} has no load balancer endpoint.")
    return cluster.lbs_inventory[0].dns_address
