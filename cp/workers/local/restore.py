import datetime as dt
import logging

from psycopg import sql
from psycopg.rows import dict_row

from ...infra import get_repo
from ...infra.db import get_pool
from ...models import (
    ClusterState,
    CommandType,
    JobState,
    PollClusterRestoreRequest,
    RestoreFullClusterRequest,
    RestoreClusterObjectRequest,
    RestoreRequest,
)
from ...services.cluster_db import connect_to_cluster_db
from ...services.storage_broker import StorageBrokerService

logger = logging.getLogger(__name__)

RESTORE_POLL_INTERVAL_SECONDS = 60
RESTORE_RUNNING_STATES = {
    "pending",
    "running",
    "paused",
    "reverting",
    "pause-requested",
    "cancel-requested",
}
RESTORE_SUCCESS_STATES = {"succeeded"}
RESTORE_FAILURE_STATES = {"failed", "canceled", "cancelled"}


def restore_cluster(
    job_id: int,
    command: RestoreRequest,
    requested_by: str,
) -> None:
    repo = get_repo()

    rr = command
    # TODO check user permissions

    # check if cluster with same cluster_id exists
    c = repo.get_cluster(rr.name, [], True)

    # TODO verify what states are appropriate for running a restore job
    if c is None or c.status != ClusterState.ACTIVE:
        repo.update_job(
            job_id,
            JobState.FAILED,
        )
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster must exist and be in an ACTIVE state for a full cluster restore.",
        )
        return

    repo.update_cluster(
        rr.name,
        requested_by,
        status=ClusterState.RESTORING,
    )

    repo.link_job_to_cluster(
        rr.name,
        job_id,
        JobState.RUNNING,
    )

    restore_cluster_worker(job_id, rr, requested_by)


def restore_full_cluster(
    job_id: int,
    command: RestoreFullClusterRequest,
    requested_by: str,
) -> None:
    repo = get_repo()

    rr = command
    target_cluster = repo.get_cluster(rr.target_cluster_id, [], True)
    if target_cluster is None or target_cluster.status != ClusterState.ACTIVE:
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The target cluster must exist and be in an ACTIVE state for recovery.",
        )
        return

    repo.update_cluster(
        rr.target_cluster_id,
        requested_by,
        status=ClusterState.RESTORING,
    )

    repo.link_job_to_cluster(
        rr.target_cluster_id,
        job_id,
        JobState.RUNNING,
    )

    restore_full_cluster_worker(job_id, rr, requested_by)


def restore_cluster_object(
    job_id: int,
    command: RestoreClusterObjectRequest,
    requested_by: str,
) -> None:
    repo = get_repo()

    rr = command
    cluster = repo.get_cluster(rr.cluster_id, [], True)

    if cluster is None or cluster.status != ClusterState.ACTIVE:
        repo.update_job(
            job_id,
            JobState.FAILED,
        )
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            "The cluster must exist and be in an ACTIVE state for an object restore.",
        )
        return

    repo.update_cluster(
        rr.cluster_id,
        requested_by,
        status=ClusterState.RESTORING,
    )

    repo.link_job_to_cluster(
        rr.cluster_id,
        job_id,
        JobState.RUNNING,
    )

    try:
        cockroach_job_id = _submit_detached_restore(
            cluster,
            backup_path=rr.backup_path,
            backup_location="external://backup",
            restore_aost=rr.restore_aost,
            object_type=rr.object_type,
            object_name=rr.object_name,
            into_db=rr.into_db,
            new_db_name=rr.new_db_name,
        )
        _record_restore_submission(
            job_id,
            rr.cluster_id,
            cockroach_job_id,
            requested_by,
        )
    except Exception as err:
        logger.exception(
            "Unhandled error while restoring object on cluster '%s'", rr.cluster_id
        )
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            1,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        repo.update_cluster(
            rr.cluster_id,
            requested_by,
            status=ClusterState.RESTORE_FAILED,
        )


def restore_full_cluster_worker(
    job_id: int,
    rr: RestoreFullClusterRequest,
    requested_by: str,
):
    repo = get_repo()
    try:
        target_cluster = repo.get_cluster(rr.target_cluster_id, [], True)
        if target_cluster is None:
            raise ValueError(f"Target cluster '{rr.target_cluster_id}' was not found.")

        backup_external_connection_uri = StorageBrokerService(
            repo
        ).get_backup_external_connection_uri(rr.source_cluster_id)
        _validate_full_cluster_backup(
            rr.backup_path,
            backup_external_connection_uri,
        )

        cockroach_job_id = _submit_detached_restore(
            target_cluster,
            backup_path=rr.backup_path,
            backup_location=backup_external_connection_uri,
            restore_aost=rr.restore_aost,
        )
        _record_restore_submission(
            job_id,
            rr.target_cluster_id,
            cockroach_job_id,
            requested_by,
        )
    except Exception as err:
        logger.exception(
            "Unhandled error while recovering cluster '%s' from '%s'",
            rr.target_cluster_id,
            rr.source_cluster_id,
        )
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        repo.update_cluster(
            rr.target_cluster_id,
            requested_by,
            status=ClusterState.RESTORE_FAILED,
        )


def _validate_full_cluster_backup(
    backup_path: str,
    backup_external_connection_uri: str,
) -> None:
    backup_path_sql = (
        sql.SQL("LATEST")
        if backup_path.upper() == "LATEST"
        else sql.Literal(backup_path)
    )
    query = sql.SQL("SELECT * FROM [SHOW BACKUP FROM {} IN {}]").format(
        backup_path_sql,
        sql.Literal(backup_external_connection_uri),
    )
    with get_pool().connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            rows = cur.execute(query).fetchall()

    if not rows:
        raise ValueError("The selected backup path was not found in source storage.")
    if not any(row.get("is_full_cluster") is True for row in rows):
        raise ValueError("The selected backup is not a full cluster backup.")


def restore_cluster_worker(
    job_id: int,
    rr: RestoreRequest,
    requested_by: str,
):
    repo = get_repo()
    try:
        cluster = repo.get_cluster(rr.name, [], True)
        if cluster is None:
            raise ValueError(f"Cluster '{rr.name}' was not found.")

        backup_location = "external://backup"
        if rr.restore_full_cluster:
            backup_external_connection_uri = StorageBrokerService(
                repo
            ).get_backup_external_connection_uri(rr.name)
            _validate_full_cluster_backup(
                rr.backup_path,
                backup_external_connection_uri,
            )
            backup_location = backup_external_connection_uri
        cockroach_job_id = _submit_detached_restore(
            cluster,
            backup_path=rr.backup_path,
            backup_location=backup_location,
            restore_aost=rr.restore_aost,
            object_type=rr.object_type,
            object_name=rr.object_name,
            new_db_name=rr.backup_into,
        )
        _record_restore_submission(
            job_id,
            rr.name,
            cockroach_job_id,
            requested_by,
        )
    except Exception as err:
        logger.exception("Unhandled error while restoring cluster '%s'", rr.name)
        repo.update_job(job_id, JobState.FAILED)
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "FAILURE",
            str(err),
        )
        repo.update_cluster(
            rr.name,
            requested_by,
            status=ClusterState.RESTORE_FAILED,
        )


def _submit_detached_restore(
    cluster,
    *,
    backup_path: str,
    backup_location: str,
    restore_aost: str | None = None,
    object_type: str | None = None,
    object_name: str | None = None,
    into_db: str | None = None,
    new_db_name: str | None = None,
) -> int:
    restore_target = sql.SQL("")
    if object_type or object_name:
        if object_type is None or object_name is None:
            raise ValueError("Both object_type and object_name are required.")
        normalized_object_type = object_type.strip().lower()
        if normalized_object_type not in {"database", "table"}:
            raise ValueError("object_type must be either 'database' or 'table'.")
        object_name_parts = [part.strip() for part in object_name.split(".")]
        if (
            not object_name_parts
            or len(object_name_parts) > 3
            or any(part == "" for part in object_name_parts)
        ):
            raise ValueError("object_name must be a valid database or table name.")
        restore_target = sql.SQL("{} {} ").format(
            sql.SQL(normalized_object_type.upper()),
            sql.Identifier(*object_name_parts),
        )

    backup_path_sql = (
        sql.SQL("LATEST")
        if backup_path.upper() == "LATEST"
        else sql.Literal(backup_path)
    )
    restore_query = sql.SQL("RESTORE {}FROM {} IN {}").format(
        restore_target,
        backup_path_sql,
        sql.Literal(backup_location),
    )
    if restore_aost:
        restore_query += sql.SQL(" AS OF SYSTEM TIME {}").format(
            sql.Literal(restore_aost)
        )

    restore_options = []
    if into_db:
        restore_options.append(sql.SQL("into_db = {}").format(sql.Literal(into_db)))
    if new_db_name:
        restore_options.append(
            sql.SQL("new_db_name = {}").format(sql.Literal(new_db_name))
        )
    restore_query += sql.SQL(" WITH ") + sql.SQL(", ").join(
        restore_options + [sql.SQL("DETACHED")]
    )

    with connect_to_cluster_db(cluster) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            row = cur.execute(restore_query).fetchone()

    if row is None or row.get("job_id") is None:
        raise RuntimeError("CockroachDB did not return a restore job id.")
    return int(row["job_id"])


def _record_restore_submission(
    cp_job_id: int,
    cluster_id: str,
    cockroach_job_id: int,
    requested_by: str,
) -> None:
    repo = get_repo()
    repo.create_task(
        cp_job_id,
        0,
        dt.datetime.now(dt.timezone.utc),
        "RESTORE_SUBMITTED",
        f"CockroachDB restore job {cockroach_job_id} was submitted.",
    )
    repo.enqueue_message(
        CommandType.POLL_CLUSTER_RESTORE,
        PollClusterRestoreRequest(
            cluster_id=cluster_id,
            cp_job_id=cp_job_id,
            cockroach_job_id=cockroach_job_id,
        ),
        requested_by,
        start_after_seconds=RESTORE_POLL_INTERVAL_SECONDS,
    )


def poll_cluster_restore(
    _msg_id: int,
    command: PollClusterRestoreRequest,
    requested_by: str,
) -> None:
    repo = get_repo()
    rr = command
    try:
        cluster = repo.get_cluster(rr.cluster_id, [], True)
        if cluster is None:
            raise ValueError(f"Cluster '{rr.cluster_id}' was not found.")

        query = sql.SQL("SHOW JOB {}").format(sql.Literal(rr.cockroach_job_id))
        with connect_to_cluster_db(cluster) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                row = cur.execute(query).fetchone()

        status = "pending" if row is None else str(row.get("status", "")).lower()
        error = None if row is None else row.get("error")

        if status in RESTORE_SUCCESS_STATES:
            repo.update_job(rr.cp_job_id, JobState.COMPLETED)
            repo.create_task(
                rr.cp_job_id,
                1,
                dt.datetime.now(dt.timezone.utc),
                "RESTORE_COMPLETED",
                f"CockroachDB restore job {rr.cockroach_job_id} completed.",
            )
            repo.update_cluster(
                rr.cluster_id,
                requested_by,
                status=ClusterState.ACTIVE,
            )
            return

        if status in RESTORE_FAILURE_STATES:
            repo.update_job(rr.cp_job_id, JobState.FAILED)
            repo.create_task(
                rr.cp_job_id,
                1,
                dt.datetime.now(dt.timezone.utc),
                "RESTORE_FAILED",
                error or f"CockroachDB restore job {rr.cockroach_job_id} failed.",
            )
            repo.update_cluster(
                rr.cluster_id,
                requested_by,
                status=ClusterState.RESTORE_FAILED,
            )
            return

        if status not in RESTORE_RUNNING_STATES:
            logger.warning(
                "CockroachDB restore job %s returned unknown status '%s'",
                rr.cockroach_job_id,
                status,
            )

        repo.update_job(rr.cp_job_id, JobState.RUNNING)
        repo.enqueue_message(
            CommandType.POLL_CLUSTER_RESTORE,
            PollClusterRestoreRequest(
                cluster_id=rr.cluster_id,
                cp_job_id=rr.cp_job_id,
                cockroach_job_id=rr.cockroach_job_id,
                poll_attempt=rr.poll_attempt + 1,
            ),
            requested_by,
            start_after_seconds=RESTORE_POLL_INTERVAL_SECONDS,
        )
    except Exception as err:
        logger.exception(
            "Unhandled error while polling restore job '%s' on cluster '%s'",
            rr.cockroach_job_id,
            rr.cluster_id,
        )
        repo.update_job(rr.cp_job_id, JobState.FAILED)
        repo.create_task(
            rr.cp_job_id,
            1,
            dt.datetime.now(dt.timezone.utc),
            "RESTORE_POLL_FAILED",
            str(err),
        )
        repo.update_cluster(
            rr.cluster_id,
            requested_by,
            status=ClusterState.RESTORE_FAILED,
        )
