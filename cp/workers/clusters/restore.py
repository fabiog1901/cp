import datetime as dt
import logging
from threading import Thread

from psycopg import sql
from psycopg.rows import dict_row

from ...infra import get_repo
from ...models import (
    ClusterState,
    CommandType,
    JobState,
    PollClusterRestoreRequest,
    PlaybookName,
    RestoreClusterObjectRequest,
    RestoreRequest,
)
from ...services.cluster_db import connect_to_cluster_db
from ...services.storage_broker import StorageBrokerService
from ..ansible import MyRunner

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
        JobState.QUEUED,
    )

    Thread(
        target=restore_cluster_worker,
        args=(
            job_id,
            rr,
            requested_by,
        ),
    ).start()


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
        object_name_parts = [part.strip() for part in rr.object_name.split(".")]
        if (
            not object_name_parts
            or len(object_name_parts) > 3
            or any(part == "" for part in object_name_parts)
        ):
            raise ValueError("object_name must be a valid database or table name.")

        backup_path = (
            sql.SQL("LATEST")
            if rr.backup_path.upper() == "LATEST"
            else sql.Literal(rr.backup_path)
        )
        restore_query = sql.SQL("RESTORE {} {} FROM {} IN {}").format(
            sql.SQL(rr.object_type.upper()),
            sql.Identifier(*object_name_parts),
            backup_path,
            sql.Literal("external://backup"),
        )
        if rr.restore_aost:
            restore_query += sql.SQL(" AS OF SYSTEM TIME {}").format(
                sql.Literal(rr.restore_aost)
            )

        restore_options = []
        if rr.into_db:
            restore_options.append(
                sql.SQL("into_db = {}").format(sql.Literal(rr.into_db))
            )
        if rr.new_db_name:
            restore_options.append(
                sql.SQL("new_db_name = {}").format(sql.Literal(rr.new_db_name))
            )
        restore_query += sql.SQL(" WITH ") + sql.SQL(", ").join(
            restore_options + [sql.SQL("DETACHED")]
        )

        with connect_to_cluster_db(cluster) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                row = cur.execute(restore_query).fetchone()

        if row is None or row.get("job_id") is None:
            raise RuntimeError("CockroachDB did not return a restore job id.")

        cockroach_job_id = int(row["job_id"])
        repo.create_task(
            job_id,
            0,
            dt.datetime.now(dt.timezone.utc),
            "RESTORE_SUBMITTED",
            f"CockroachDB restore job {cockroach_job_id} was submitted.",
        )

        repo.enqueue_message(
            CommandType.POLL_CLUSTER_RESTORE,
            PollClusterRestoreRequest(
                cluster_id=rr.cluster_id,
                cp_job_id=job_id,
                cockroach_job_id=cockroach_job_id,
            ),
            requested_by,
            start_after_seconds=RESTORE_POLL_INTERVAL_SECONDS,
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


def restore_cluster_worker(
    job_id: int,
    rr: RestoreRequest,
    requested_by: str,
):
    repo = get_repo()
    try:
        backup_external_connection_uri = StorageBrokerService(
            repo
        ).get_backup_external_connection_uri(rr.name)
        extra_vars = {
            "deployment_id": rr.name,
            "backup_path": rr.backup_path,
            "restore_aost": rr.restore_aost,
            "restore_full_cluster": rr.restore_full_cluster,
            "object_type": rr.object_type,
            "object_name": rr.object_name,
            "backup_into": rr.backup_into,
            "backup_external_connection_uri": backup_external_connection_uri,
        }

        job_status, _, _ = MyRunner(job_id).launch_runner(
            PlaybookName.RESTORE_CLUSTER, extra_vars
        )

        if job_status != "successful":
            repo.update_cluster(
                rr.name,
                requested_by,
                status=ClusterState.RESTORE_FAILED,
            )
            return

        repo.update_cluster(
            rr.name,
            requested_by,
            status=ClusterState.ACTIVE,
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
