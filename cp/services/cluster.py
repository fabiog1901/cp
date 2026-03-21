"""Business logic for the clusters vertical."""

from pydantic import ValidationError

from ..infra.errors import RepositoryError
from ..models import Cluster, ClusterScaleRequest, ClusterUpgradeRequest, JobID, JobType, RestoreRequest
from ..repos.postgres import cluster_jobs_repo, cluster_repo, event_repo, mq_repo
from .errors import ServiceValidationError, from_repository_error


def list_visible_clusters(groups: list[str], is_admin: bool) -> list:
    try:
        return cluster_repo.list_clusters(groups, is_admin)
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Clusters are temporarily unavailable.",
            fallback_message="Unable to load clusters.",
        ) from err


def get_cluster_for_user(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> Cluster | None:
    try:
        return cluster_repo.get_cluster(cluster_id, groups, is_admin)
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster details are temporarily unavailable.",
            fallback_message=f"Unable to load cluster '{cluster_id}'.",
        ) from err


def list_cluster_jobs_for_user(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
):
    selected_cluster = get_cluster_for_user(cluster_id, groups, is_admin)
    if selected_cluster is None:
        return None, []
    try:
        return selected_cluster, cluster_jobs_repo.list_cluster_jobs(cluster_id)
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster jobs are temporarily unavailable.",
            fallback_message=f"Unable to load jobs for cluster '{cluster_id}'.",
        ) from err


def get_create_dialog_options() -> dict:
    try:
        return {
            "versions": [x.version for x in cluster_repo.list_versions()],
            "node_counts": [x.node_count for x in cluster_repo.list_node_counts()],
            "cpus_per_node": [x.cpu_count for x in cluster_repo.list_cpus_per_node()],
            "disk_sizes": [x.size_gb for x in cluster_repo.list_disk_sizes()],
            "regions": cluster_repo.list_regions(),
        }
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster options are temporarily unavailable.",
            fallback_message="Unable to load cluster options.",
        ) from err


def get_cluster_dialog_options(selected_cluster: Cluster) -> dict:
    all_new_versions = [
        x.version for x in cluster_repo.list_upgrade_versions(selected_cluster.version[:5])
    ]

    major_yy, major_mm, _ = [int(x) for x in selected_cluster.version[1:].split(".")]
    available_versions = []
    for version in all_new_versions:
        f1, f2, _ = [int(x) for x in version[1:].split(".")]
        if major_yy == f1 and major_mm == f2:
            available_versions.append(version)
            continue
        if major_yy == f1 and major_mm in [1, 3] and f2 == major_mm + 1:
            available_versions.append(version)
            continue
        if major_yy == f1 and major_mm == 2 and f2 in [3, 4]:
            available_versions.append(version)
            continue
        if major_yy + 1 == f1 and major_mm == 4 and f2 in [1, 2]:
            available_versions.append(version)

    try:
        return {
            "node_counts": [x.node_count for x in cluster_repo.list_node_counts()],
            "cpus_per_node": [x.cpu_count for x in cluster_repo.list_cpus_per_node()],
            "disk_sizes": [x.size_gb for x in cluster_repo.list_disk_sizes()],
            "regions": cluster_repo.list_regions(),
            "upgrade_versions": available_versions,
        }
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster options are temporarily unavailable.",
            fallback_message="Unable to load cluster update options.",
        ) from err


def _normalize_cluster_name(name: str) -> str:
    return "".join([x.lower() for x in name if x.lower() in "-abcdefghijklmnopqrstuvwxyz"])


def request_cluster_creation(
    form_data: dict,
    selected_cpus_per_node: int,
    selected_disk_size: int,
    selected_node_count: int,
    selected_regions: list[str],
    selected_version: str,
    selected_group: str,
    requested_by: str,
) -> int:
    payload = dict(form_data)
    payload["node_cpus"] = selected_cpus_per_node
    payload["disk_size"] = selected_disk_size
    payload["node_count"] = selected_node_count
    payload["regions"] = list(selected_regions)
    payload["version"] = selected_version
    payload["group"] = selected_group
    payload["name"] = _normalize_cluster_name(payload["name"])

    try:
        msg_id: JobID = mq_repo.insert_into_mq(
            JobType.CREATE_CLUSTER,
            payload,
            requested_by,
        )
        event_repo.insert_event_log(
            requested_by,
            JobType.CREATE_CLUSTER,
            payload | {"job_id": msg_id.job_id},
        )
        return msg_id.job_id
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster creation could not be requested right now.",
            validation_message="The cluster request contains invalid data.",
            fallback_message="Unable to request cluster creation.",
        ) from err


def request_cluster_deletion(cluster_id: str, requested_by: str) -> int:
    try:
        msg_id: JobID = mq_repo.insert_into_mq(
            JobType.DELETE_CLUSTER,
            {"cluster_id": cluster_id},
            requested_by,
        )
        event_repo.insert_event_log(
            requested_by,
            JobType.DELETE_CLUSTER,
            {"cluster_id": cluster_id, "job_id": msg_id.job_id},
        )
        return msg_id.job_id
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster deletion could not be requested right now.",
            fallback_message=f"Unable to request deletion of cluster '{cluster_id}'.",
        ) from err


def request_cluster_scale(
    cluster_id: str,
    selected_cpus_per_node: int,
    selected_disk_size: int,
    selected_node_count: int,
    selected_regions: list[str],
    requested_by: str,
) -> int:
    payload = ClusterScaleRequest(
        name=cluster_id,
        node_cpus=selected_cpus_per_node,
        disk_size=selected_disk_size,
        node_count=selected_node_count,
        regions=list(selected_regions),
    ).model_dump()

    try:
        msg_id: JobID = mq_repo.insert_into_mq(
            JobType.SCALE_CLUSTER,
            payload,
            requested_by,
        )
        event_repo.insert_event_log(
            requested_by,
            JobType.SCALE_CLUSTER,
            payload | {"job_id": msg_id.job_id},
        )
        return msg_id.job_id
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster scaling could not be requested right now.",
            validation_message="The cluster scale request contains invalid data.",
            fallback_message=f"Unable to request scaling for cluster '{cluster_id}'.",
        ) from err


def request_cluster_upgrade(
    cluster_id: str,
    selected_version: str,
    auto_finalize: bool,
    requested_by: str,
) -> int:
    payload = ClusterUpgradeRequest(
        name=cluster_id,
        version=selected_version,
        auto_finalize=auto_finalize,
    ).model_dump()

    try:
        msg_id: JobID = mq_repo.insert_into_mq(
            JobType.UPGRADE_CLUSTER,
            payload,
            requested_by,
        )
        event_repo.insert_event_log(
            requested_by,
            JobType.UPGRADE_CLUSTER,
            payload | {"job_id": msg_id.job_id},
        )
        return msg_id.job_id
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster upgrade could not be requested right now.",
            validation_message="The cluster upgrade request contains invalid data.",
            fallback_message=f"Unable to request upgrade for cluster '{cluster_id}'.",
        ) from err


def request_cluster_restore(
    cluster_id: str,
    backup_path: str,
    restore_aost: str | None,
    restore_full_cluster: bool,
    object_type: str | None,
    object_name: str | None,
    backup_into: str | None,
    requested_by: str,
) -> int:
    payload = RestoreRequest(
        name=cluster_id,
        backup_path=backup_path,
        restore_aost=restore_aost,
        restore_full_cluster=restore_full_cluster,
        object_type=object_type,
        object_name=object_name,
        backup_into=backup_into,
    ).model_dump()

    try:
        msg_id: JobID = mq_repo.insert_into_mq(
            JobType.RESTORE_CLUSTER,
            payload,
            requested_by,
        )
        event_repo.insert_event_log(
            requested_by,
            JobType.RESTORE_CLUSTER,
            payload | {"job_id": msg_id.job_id},
        )
        return msg_id.job_id
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster restore could not be requested right now.",
            validation_message="The cluster restore request contains invalid data.",
            fallback_message=f"Unable to request restore for cluster '{cluster_id}'.",
        ) from err


def validate_restore_request(**kwargs) -> dict:
    try:
        return RestoreRequest(**kwargs).model_dump()
    except ValidationError as err:
        msg = err.errors()[0].get("msg", "Restore request is invalid.")
        raise ServiceValidationError(
            msg,
            title="Invalid Restore Request",
        ) from err
