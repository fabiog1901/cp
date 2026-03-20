"""Business logic for the clusters vertical."""

from pydantic import ValidationError

from ..models import Cluster, ClusterScaleRequest, ClusterUpgradeRequest, JobID, JobType, RestoreRequest
from ..repos.postgres import cluster_jobs, cluster, events, mq


def list_visible_clusters(groups: list[str], is_admin: bool) -> list:
    return cluster.list_clusters(groups, is_admin)


def get_cluster_for_user(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> Cluster | None:
    return cluster.get_cluster(cluster_id, groups, is_admin)


def list_cluster_jobs_for_user(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
):
    cluster = get_cluster_for_user(cluster_id, groups, is_admin)
    if cluster is None:
        return None, []
    return cluster, cluster_jobs.list_cluster_jobs(cluster_id)


def get_create_dialog_options() -> dict:
    return {
        "versions": [x.version for x in cluster.list_versions()],
        "node_counts": [x.node_count for x in cluster.list_node_counts()],
        "cpus_per_node": [x.cpu_count for x in cluster.list_cpus_per_node()],
        "disk_sizes": [x.size_gb for x in cluster.list_disk_sizes()],
        "regions": cluster.list_regions(),
    }


def get_cluster_dialog_options(cluster: Cluster) -> dict:
    all_new_versions = [
        x.version for x in cluster.list_upgrade_versions(cluster.version[:5])
    ]

    major_yy, major_mm, _ = [int(x) for x in cluster.version[1:].split(".")]
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

    return {
        "node_counts": [x.node_count for x in cluster.list_node_counts()],
        "cpus_per_node": [x.cpu_count for x in cluster.list_cpus_per_node()],
        "disk_sizes": [x.size_gb for x in cluster.list_disk_sizes()],
        "regions": cluster.list_regions(),
        "upgrade_versions": available_versions,
    }


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

    msg_id: JobID = mq.insert_into_mq(
        JobType.CREATE_CLUSTER,
        payload,
        requested_by,
    )
    events.insert_event_log(
        requested_by,
        JobType.CREATE_CLUSTER,
        payload | {"job_id": msg_id.job_id},
    )
    return msg_id.job_id


def request_cluster_deletion(cluster_id: str, requested_by: str) -> int:
    msg_id: JobID = mq.insert_into_mq(
        JobType.DELETE_CLUSTER,
        {"cluster_id": cluster_id},
        requested_by,
    )
    events.insert_event_log(
        requested_by,
        JobType.DELETE_CLUSTER,
        {"cluster_id": cluster_id, "job_id": msg_id.job_id},
    )
    return msg_id.job_id


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

    msg_id: JobID = mq.insert_into_mq(
        JobType.SCALE_CLUSTER,
        payload,
        requested_by,
    )
    events.insert_event_log(
        requested_by,
        JobType.SCALE_CLUSTER,
        payload | {"job_id": msg_id.job_id},
    )
    return msg_id.job_id


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

    msg_id: JobID = mq.insert_into_mq(
        JobType.UPGRADE_CLUSTER,
        payload,
        requested_by,
    )
    events.insert_event_log(
        requested_by,
        JobType.UPGRADE_CLUSTER,
        payload | {"job_id": msg_id.job_id},
    )
    return msg_id.job_id


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

    msg_id: JobID = mq.insert_into_mq(
        JobType.RESTORE_CLUSTER,
        payload,
        requested_by,
    )
    events.insert_event_log(
        requested_by,
        JobType.RESTORE_CLUSTER,
        payload | {"job_id": msg_id.job_id},
    )
    return msg_id.job_id


def validate_restore_request(**kwargs) -> dict:
    try:
        return RestoreRequest(**kwargs).model_dump()
    except ValidationError:
        raise
