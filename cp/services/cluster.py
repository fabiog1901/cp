"""Business logic for the clusters vertical."""

from pydantic import ValidationError

from ..infra.errors import RepositoryError
from ..models import (
    AuditEvent,
    Cluster,
    ClusterPublic,
    ClusterScaleRequest,
    ClusterStatsResponse,
    ClusterUpgradeRequest,
    CommandType,
    CreateClusterCommand,
    DeleteClusterCommand,
    JobID,
    RestoreRequest,
    to_public_cluster,
)
from ..repos.base import BaseRepo
from .base import log_event
from .errors import ServiceValidationError, from_repository_error


class ClusterService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def list_visible_clusters(self, groups: list[str], is_admin: bool) -> list:
        try:
            return self.repo.list_clusters(groups, is_admin)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Clusters are temporarily unavailable.",
                fallback_message="Unable to load clusters.",
            ) from err

    def get_visible_cluster_stats(
        self, groups: list[str], is_admin: bool
    ) -> ClusterStatsResponse:
        try:
            return self.repo.get_cluster_stats(groups, is_admin)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster stats are temporarily unavailable.",
                fallback_message="Unable to load cluster stats.",
            ) from err

    def get_cluster_for_user(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
    ) -> ClusterPublic | None:
        try:
            cluster = self.repo.get_cluster(cluster_id, groups, is_admin)
            if cluster is None:
                return None
            return to_public_cluster(cluster)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster details are temporarily unavailable.",
                fallback_message=f"Unable to load cluster '{cluster_id}'.",
            ) from err

    def list_cluster_jobs_for_user(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
    ) -> tuple[ClusterPublic | None, list]:
        selected_cluster = self.get_cluster_for_user(
            cluster_id,
            groups,
            is_admin,
        )
        if selected_cluster is None:
            return None, []
        try:
            return selected_cluster, self.repo.list_cluster_jobs(cluster_id)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster jobs are temporarily unavailable.",
                fallback_message=f"Unable to load jobs for cluster '{cluster_id}'.",
            ) from err

    def get_create_dialog_options(self) -> dict:
        try:
            return {
                "versions": [x.version for x in self.repo.list_versions()],
                "node_counts": [x.node_count for x in self.repo.list_node_counts()],
                "cpus_per_node": [x.cpu_count for x in self.repo.list_cpus_per_node()],
                "disk_sizes": [x.size_gb for x in self.repo.list_disk_sizes()],
                "regions": self.repo.list_region_options(),
            }
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster options are temporarily unavailable.",
                fallback_message="Unable to load cluster options.",
            ) from err

    def get_cluster_dialog_options(self, selected_cluster: Cluster) -> dict:
        all_new_versions = [
            x.version
            for x in self.repo.list_upgrade_versions(selected_cluster.version[:5])
        ]

        major_yy, major_mm, _ = [
            int(x) for x in selected_cluster.version[1:].split(".")
        ]
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
                "node_counts": [x.node_count for x in self.repo.list_node_counts()],
                "cpus_per_node": [x.cpu_count for x in self.repo.list_cpus_per_node()],
                "disk_sizes": [x.size_gb for x in self.repo.list_disk_sizes()],
                "regions": self.repo.list_region_options(),
                "upgrade_versions": available_versions,
            }
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster options are temporarily unavailable.",
                fallback_message="Unable to load cluster update options.",
            ) from err

    @staticmethod
    def _normalize_cluster_name(name: str) -> str:
        return "".join(
            [x.lower() for x in name if x.lower() in "-abcdefghijklmnopqrstuvwxyz"]
        )

    def enqueue_cluster_creation(
        self,
        form_data: dict,
        selected_cpus_per_node: int,
        selected_disk_size: int,
        selected_node_count: int,
        selected_regions: list[str],
        selected_version: str,
        selected_group: str,
        requested_by: str,
    ) -> int:
        payload = CreateClusterCommand(
            name=self._normalize_cluster_name(form_data["name"]),
            node_cpus=selected_cpus_per_node,
            disk_size=selected_disk_size,
            node_count=selected_node_count,
            regions=list(selected_regions),
            version=selected_version,
            group=selected_group,
        )

        try:
            msg_id: JobID = self.repo.enqueue_command(
                CommandType.CREATE_CLUSTER,
                payload,
                requested_by,
            )
            log_event(
                self.repo,
                requested_by,
                AuditEvent.CLUSTER_CREATE_REQUESTED,
                payload.model_dump() | {"job_id": msg_id.job_id},
            )
            return msg_id.job_id
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster creation could not be requested right now.",
                validation_message="The cluster request contains invalid data.",
                fallback_message="Unable to request cluster creation.",
            ) from err

    def enqueue_cluster_deletion(self, cluster_id: str, requested_by: str) -> int:
        try:
            msg_id: JobID = self.repo.enqueue_command(
                CommandType.DELETE_CLUSTER,
                DeleteClusterCommand(cluster_id=cluster_id),
                requested_by,
            )
            log_event(
                self.repo,
                requested_by,
                AuditEvent.CLUSTER_DELETE_REQUESTED,
                {"cluster_id": cluster_id, "job_id": msg_id.job_id},
            )
            return msg_id.job_id
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster deletion could not be requested right now.",
                fallback_message=f"Unable to request deletion of cluster '{cluster_id}'.",
            ) from err

    def enqueue_cluster_scale(
        self,
        request: ClusterScaleRequest,
        requested_by: str,
    ) -> int:
        payload = request

        try:
            msg_id: JobID = self.repo.enqueue_command(
                CommandType.SCALE_CLUSTER,
                payload,
                requested_by,
            )
            log_event(
                self.repo,
                requested_by,
                AuditEvent.CLUSTER_SCALE_REQUESTED,
                payload.model_dump() | {"job_id": msg_id.job_id},
            )
            return msg_id.job_id
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster scaling could not be requested right now.",
                validation_message="The cluster scale request contains invalid data.",
                fallback_message=f"Unable to request scaling for cluster '{request.name}'.",
            ) from err

    def enqueue_cluster_upgrade(
        self,
        request: ClusterUpgradeRequest,
        requested_by: str,
    ) -> int:
        payload = request

        try:
            msg_id: JobID = self.repo.enqueue_command(
                CommandType.UPGRADE_CLUSTER,
                payload,
                requested_by,
            )
            log_event(
                self.repo,
                requested_by,
                AuditEvent.CLUSTER_UPGRADE_REQUESTED,
                payload.model_dump() | {"job_id": msg_id.job_id},
            )
            return msg_id.job_id
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster upgrade could not be requested right now.",
                validation_message="The cluster upgrade request contains invalid data.",
                fallback_message=f"Unable to request upgrade for cluster '{request.name}'.",
            ) from err

    def enqueue_cluster_restore(
        self,
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
        )

        try:
            msg_id: JobID = self.repo.enqueue_command(
                CommandType.RESTORE_CLUSTER,
                payload,
                requested_by,
            )
            log_event(
                self.repo,
                requested_by,
                AuditEvent.CLUSTER_RESTORE_REQUESTED,
                payload.model_dump() | {"job_id": msg_id.job_id},
            )
            return msg_id.job_id
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster restore could not be requested right now.",
                validation_message="The cluster restore request contains invalid data.",
                fallback_message=f"Unable to request restore for cluster '{cluster_id}'.",
            ) from err

    @staticmethod
    def validate_restore_request(**kwargs) -> dict:
        try:
            return RestoreRequest(**kwargs).model_dump()
        except ValidationError as err:
            msg = err.errors()[0].get("msg", "Restore request is invalid.")
            raise ServiceValidationError(
                msg,
                title="Invalid Restore Request",
            ) from err
