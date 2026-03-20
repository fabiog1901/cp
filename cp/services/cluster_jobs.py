"""Business logic for the cluster jobs vertical."""

from ..models import ClusterJobsSnapshot
from ..repos.postgres import cluster
from . import cluster


def load_cluster_jobs_snapshot(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> ClusterJobsSnapshot | None:
    cluster = cluster.get_cluster_for_user(cluster_id, groups, is_admin)
    if cluster is None:
        return None

    return ClusterJobsSnapshot(
        cluster=cluster,
        jobs=cluster.list_cluster_jobs(cluster_id),
    )
