"""Business logic for the cluster users vertical."""

from pydantic import ValidationError

from ..infra.errors import RepositoryError
from ..models import Cluster, ClusterUsersSnapshot, EventType, NewDatabaseUserRequest
from ..repos.postgres.cluster_users_repo import ClusterUsersRepo
from ..repos.postgres.event_repo import EventRepo
from .cluster import ClusterService
from .errors import ServiceNotFoundError, ServiceValidationError, from_repository_error


def load_cluster_users_snapshot(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> ClusterUsersSnapshot | None:
    selected_cluster = ClusterService.get_cluster_for_user(cluster_id, groups, is_admin)
    if selected_cluster is None:
        return None

    try:
        return ClusterUsersSnapshot(
            cluster=selected_cluster,
            database_users=ClusterUsersRepo.list_database_users(
                _get_primary_dns_address(selected_cluster)
            ),
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Database users are temporarily unavailable.",
            fallback_message=f"Unable to load database users for cluster '{cluster_id}'.",
        ) from err


def create_database_user(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    username: str,
    password: str,
    requested_by: str,
) -> None:
    selected_cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    try:
        request = NewDatabaseUserRequest(username=username, password=password)
    except ValidationError as err:
        raise ServiceValidationError("Database username or password is invalid.") from err

    try:
        ClusterUsersRepo.create_database_user(
            _get_primary_dns_address(selected_cluster),
            request.username,
            request.password,
        )
        EventRepo.insert_event_log(
            requested_by,
            EventType.DB_USER_ADD,
            {"cluster_id": selected_cluster.cluster_id, "db_user": request.username},
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Database user creation is temporarily unavailable.",
            conflict_message=f"Database user '{request.username}' already exists.",
            validation_message="Database user details are invalid.",
            fallback_message=f"Unable to create database user '{request.username}'.",
        ) from err


def remove_database_user(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    username: str,
    requested_by: str,
) -> None:
    selected_cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    try:
        ClusterUsersRepo.remove_database_user(
            _get_primary_dns_address(selected_cluster),
            username,
        )
        EventRepo.insert_event_log(
            requested_by,
            EventType.DB_USER_REMOVE,
            {"cluster_id": selected_cluster.cluster_id, "db_user": username},
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Database user removal is temporarily unavailable.",
            fallback_message=f"Unable to remove database user '{username}'.",
        ) from err


def revoke_database_user_role(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    username: str,
    role: str,
    requested_by: str,
) -> None:
    selected_cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    try:
        ClusterUsersRepo.revoke_database_user_role(
            _get_primary_dns_address(selected_cluster),
            username,
            role,
        )
        EventRepo.insert_event_log(
            requested_by,
            EventType.DB_USER_REMOVE_ROLE,
            {"cluster_id": selected_cluster.cluster_id, "db_user": username, "role": role},
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Database role updates are temporarily unavailable.",
            fallback_message=f"Unable to revoke role '{role}' from '{username}'.",
        ) from err


def update_database_user_password(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    username: str,
    password: str,
    requested_by: str,
) -> None:
    if not password:
        raise ServiceValidationError("Password is required.")

    selected_cluster = _get_cluster_or_raise(cluster_id, groups, is_admin)
    try:
        ClusterUsersRepo.update_database_user_password(
            _get_primary_dns_address(selected_cluster),
            username,
            password,
        )
        EventRepo.insert_event_log(
            requested_by,
            EventType.DB_USER_UPDATE,
            {"cluster_id": selected_cluster.cluster_id, "db_user": username},
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Password updates are temporarily unavailable.",
            validation_message="The new password is invalid.",
            fallback_message=f"Unable to update password for '{username}'.",
        ) from err


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
