import asyncio
import datetime as dt
import logging
import random
from typing import Callable

from psycopg.rows import class_row

from ..infra import get_repo
from ..infra.db import get_pool
from ..models import (
    ClusterState,
    CommandModel,
    CommandType,
    FailZombieJobsCommand,
    JobState,
    Msg,
    Nodes,
    parse_command_payload,
)
from .clusters.create import create_cluster
from .clusters.delete import delete_cluster
from .clusters.healthcheck import healthcheck_clusters
from .clusters.restore import restore_cluster
from .clusters.scale import scale_cluster
from .clusters.upgrade import upgrade_cluster

logger = logging.getLogger(__name__)


def fail_zombie_jobs(
    _job_id: int,
    _command: FailZombieJobsCommand,
    _requested_by: str,
):
    get_repo().fail_zombie_jobs()


CommandHandler = Callable[[int, CommandModel, str], None]

COMMAND_HANDLERS: dict[CommandType, CommandHandler] = {
    CommandType.CREATE_CLUSTER: create_cluster,
    CommandType.RECREATE_CLUSTER: lambda job_id, command, requested_by: create_cluster(
        job_id, command, requested_by, True
    ),
    CommandType.DELETE_CLUSTER: delete_cluster,
    CommandType.SCALE_CLUSTER: scale_cluster,
    CommandType.UPGRADE_CLUSTER: upgrade_cluster,
    CommandType.RESTORE_CLUSTER: restore_cluster,
    CommandType.FAIL_ZOMBIE_JOBS: fail_zombie_jobs,
    CommandType.HEALTHCHECK_CLUSTERS: healthcheck_clusters,
}


def get_nodes():

    rs: list[Nodes] = []
    active_cluster_ids: set[str] = set()

    try:
        active_cluster_ids = {
            cluster.cluster_id
            for cluster in get_repo().list_clusters([], True)
            if cluster.status
            not in {
                ClusterState.DELETING.value,
                ClusterState.DELETED.value,
            }
        }
        rs = get_repo().list_cluster_nodes()
    except Exception as e:
        print("Error", str(e))

    return [
        {"targets": [f"{n}:8080" for n in x.nodes], "labels": {"cluster": x.cluster_id}}
        for x in rs
        if x.cluster_id in active_cluster_ids
    ]


async def pull_from_mq():
    try:
        while True:
            await asyncio.sleep(5 * random.uniform(0.7, 1.3))
            try:
                with get_pool().connection() as conn:
                    with conn.cursor(row_factory=class_row(Msg)) as cur:
                        with conn.transaction():
                            msg = cur.execute("""
                                SELECT * 
                                FROM mq 
                                WHERE now() > start_after 
                                LIMIT 1 
                                FOR UPDATE SKIP LOCKED
                                """).fetchone()

                            if msg is None:
                                continue

                            logger.info(
                                "Processing MQ message %s of type %s",
                                msg.msg_id,
                                msg.msg_type,
                            )
                            repo = get_repo()

                            try:
                                handler = COMMAND_HANDLERS.get(msg.msg_type)
                                if handler is None:
                                    raise ValueError(
                                        f"Unknown task type requested: {msg.msg_type}"
                                    )

                                command = parse_command_payload(
                                    msg.msg_type,
                                    msg.msg_data,
                                )
                                handler(msg.msg_id, command, msg.created_by)

                                if msg.msg_type == CommandType.HEALTHCHECK_CLUSTERS:
                                    cur.execute(
                                        """
                                        INSERT INTO mq (msg_type, start_after) 
                                        VALUES (%s, now() + INTERVAL '60s' + (random()*10)::INTERVAL)
                                        """,
                                        (CommandType.HEALTHCHECK_CLUSTERS.value,),
                                    )
                            except Exception as err:
                                logger.exception(
                                    "MQ message %s failed during dispatch",
                                    msg.msg_id,
                                )
                                try:
                                    repo.update_job(msg.msg_id, JobState.FAILED)
                                except Exception:
                                    logger.exception(
                                        "Unable to mark job %s as failed",
                                        msg.msg_id,
                                    )
                                try:
                                    repo.create_task(
                                        msg.msg_id,
                                        0,
                                        dt.datetime.now(dt.timezone.utc),
                                        "FAILURE",
                                        str(err),
                                    )
                                except Exception:
                                    logger.exception(
                                        "Unable to record failure task for job %s",
                                        msg.msg_id,
                                    )
                            finally:
                                cur.execute(
                                    "DELETE FROM mq WHERE msg_id = %s;",
                                    (msg.msg_id,),
                                )
            except Exception:
                logger.exception("Unexpected failure while polling the message queue")

    except asyncio.CancelledError:
        logger.info("Task pull_from_mq was stopped")
