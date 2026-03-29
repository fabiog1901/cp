"""Business logic for the cluster backups vertical."""

from ..infra.errors import RepositoryError
from ..models import BackupDetails, Cluster, ClusterBackupsSnapshot
from ..repos.base import BaseRepo
from .base import log_event
from .errors import ServiceNotFoundError, ServiceValidationError, from_repository_error


class ClusterBackupsService:
    def __init__(self, repo: BaseRepo):
        self.repo = repo

    def load_cluster_backups_snapshot(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
    ) -> ClusterBackupsSnapshot | None:
        selected_cluster = self.repo.get_cluster(cluster_id, groups, is_admin)
        if selected_cluster is None:
            return None

        try:
            return ClusterBackupsSnapshot(
                cluster=selected_cluster,
                backup_paths=self.repo.list_backup_paths(
                    self._get_primary_dns_address(selected_cluster)
                ),
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Cluster backups are temporarily unavailable.",
                fallback_message=f"Unable to load backups for cluster '{cluster_id}'.",
            ) from err

    def load_backup_details(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
        backup_path: str,
    ) -> list[BackupDetails]:
        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        try:
            return self.repo.list_backup_details(
                self._get_primary_dns_address(selected_cluster),
                backup_path,
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Backup details are temporarily unavailable.",
                fallback_message=f"Unable to load backup details for cluster '{cluster_id}'.",
            ) from err

    def enqueue_cluster_restore(
        self,
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
        selected_cluster = self._get_cluster_or_raise(
            cluster_id,
            groups,
            is_admin,
        )
        restore_request = self.validate_restore_request(
            name=selected_cluster.cluster_id,
            backup_path=backup_path,
            restore_aost=restore_aost,
            restore_full_cluster=restore_full_cluster,
            object_type=object_type,
            object_name=object_name,
            backup_into=backup_into,
        )

        return self._enqueue_cluster_restore(
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
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool,
    ) -> Cluster:
        selected_cluster = self.repo.get_cluster(cluster_id, groups, is_admin)
        if selected_cluster is None:
            raise ServiceNotFoundError(f"Cluster '{cluster_id}' was not found.")
        return selected_cluster

    def _enqueue_cluster_restore(
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
        from ..models import JobID, JobType, RestoreRequest

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
            msg_id: JobID = self.repo.enqueue_job(
                JobType.RESTORE_CLUSTER,
                payload,
                requested_by,
            )
            log_event(
                self.repo,
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

    @staticmethod
    def validate_restore_request(**kwargs) -> dict:
        from pydantic import ValidationError

        from ..models import RestoreRequest

        try:
            return RestoreRequest(**kwargs).model_dump()
        except ValidationError as err:
            msg = err.errors()[0].get("msg", "Restore request is invalid.")
            raise ServiceValidationError(
                msg,
                title="Invalid Restore Request",
            ) from err

    @staticmethod
    def _get_primary_dns_address(cluster: Cluster) -> str:
        if not cluster.lbs_inventory:
            raise ServiceValidationError(
                f"Cluster '{cluster.cluster_id}' has no load balancer endpoint."
            )
        return cluster.lbs_inventory[0].dns_address
