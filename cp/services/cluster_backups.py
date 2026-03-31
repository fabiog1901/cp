"""Business logic for the cluster backups vertical."""

import logging

import psycopg
from psycopg import sql
from psycopg.rows import class_row

from ..infra.db import translate_database_error
from ..infra.util import decrypt_secret
from ..infra.errors import RepositoryError
from ..models import BackupDetails, BackupPathOption, Cluster, ClusterBackupsSnapshot
from ..repos.base import BaseRepo
from .base import log_event
from .errors import ServiceNotFoundError, ServiceValidationError, from_repository_error

CONNECT_TIMEOUT_SECS = 2
CLUSTER_DB_PORT = 26257
CLUSTER_DB_NAME = "defaultdb"
CLUSTER_DB_USERNAME = "cockroach"
logger = logging.getLogger(__name__)


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
                backup_paths=self._list_backup_paths(
                    self._get_primary_dns_address(selected_cluster),
                    self._get_cluster_db_password(selected_cluster),
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
            return self._list_backup_details(
                self._get_primary_dns_address(selected_cluster),
                self._get_cluster_db_password(selected_cluster),
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
        from ..models import AuditEvent, CommandType, JobID, RestoreRequest

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

    def _list_backup_paths(
        self, dns_address: str, password: str
    ) -> list[BackupPathOption]:
        try:
            with self._connect(dns_address, password) as conn:
                with conn.cursor() as cur:
                    rows = cur.execute(
                        "SHOW BACKUPS IN 'external://backup';"
                    ).fetchall()
        except Exception as err:
            logger.debug(
                "Cluster backup query failed [operation=cluster_backups.list_backup_paths]"
            )
            raise translate_database_error(
                err, "cluster_backups.list_backup_paths"
            ) from err

        paths = sorted((str(row[0]) for row in rows), reverse=True)
        return [BackupPathOption(path="LATEST")] + [
            BackupPathOption(path=path) for path in paths
        ]

    def _list_backup_details(
        self,
        dns_address: str,
        password: str,
        backup_path: str,
    ) -> list[BackupDetails]:
        query = sql.SQL(
            """
            SELECT database_name, parent_schema_name, object_name,
                object_type, backup_type, start_time, end_time
            FROM [SHOW BACKUP {} IN 'external://backup']
            WHERE (
                database_name NOT IN ('system', 'postgres')
                and object_name NOT IN ('system', 'postgres')
            )

            """
        ).format(sql.Literal(backup_path))

        try:
            with self._connect(dns_address, password) as conn:
                with conn.cursor(row_factory=class_row(BackupDetails)) as cur:
                    return cur.execute(query).fetchall()
        except Exception as err:
            logger.debug(
                "Cluster backup query failed [operation=cluster_backups.list_backup_details]"
            )
            raise translate_database_error(
                err, "cluster_backups.list_backup_details"
            ) from err

    def _get_cluster_db_password(self, cluster: Cluster) -> str:
        if cluster.password is None:
            raise ServiceValidationError(
                f"Cluster '{cluster.cluster_id}' has no database password configured."
            )
        try:
            return decrypt_secret(cluster.password).decode("utf-8")
        except Exception as err:
            raise ServiceValidationError(
                f"Cluster '{cluster.cluster_id}' has an invalid database password."
            ) from err

    @staticmethod
    def _connect(dns_address: str, password: str) -> psycopg.Connection:
        return psycopg.connect(
            (
                f"postgres://{CLUSTER_DB_USERNAME}:{password}"
                f"@{dns_address}:{CLUSTER_DB_PORT}/{CLUSTER_DB_NAME}?sslmode=require"
            ),
            autocommit=True,
            connect_timeout=CONNECT_TIMEOUT_SECS,
        )
