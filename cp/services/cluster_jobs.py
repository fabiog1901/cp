"""Business logic for the cluster jobs vertical."""

from ..infra.errors import RepositoryError
from ..models import ClusterJobsSnapshot
from ..repos.postgres.cluster_repo import ClusterRepo
from .cluster import ClusterService
from .errors import from_repository_error


def load_cluster_jobs_snapshot(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
) -> ClusterJobsSnapshot | None:
    selected_cluster = ClusterService.get_cluster_for_user(cluster_id, groups, is_admin)
    if selected_cluster is None:
        return None

    try:
        return ClusterJobsSnapshot(
            cluster=selected_cluster,
            jobs=ClusterRepo.list_cluster_jobs(cluster_id),
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Cluster jobs are temporarily unavailable.",
            fallback_message=f"Unable to load jobs for cluster '{cluster_id}'.",
        ) from err
