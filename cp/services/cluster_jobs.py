"""Business logic for the cluster jobs vertical."""

from cpkit import get_repo
from cpkit.errors import RepositoryError, from_repository_error

from ..models import ClusterJobsSnapshot, to_public_cluster


class ClusterJobsService:
    def __init__(self) -> None:
        self.repo = get_repo()

    def load_cluster_jobs_snapshot(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
    ) -> ClusterJobsSnapshot | None:
        selected_cluster = self.repo.get_cluster(cluster_id, groups, is_admin)
        if selected_cluster is None:
            return None

        try:
            return ClusterJobsSnapshot(
                cluster=to_public_cluster(selected_cluster),
                jobs=self.repo.list_cluster_jobs(cluster_id),
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster jobs are temporarily unavailable.",
                fallback_message=f"Unable to load jobs for cluster '{cluster_id}'.",
            ) from err
