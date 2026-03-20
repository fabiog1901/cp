import asyncio
import datetime as dt
import logging
import random

from psycopg.rows import class_row

from ..models import JobState, JobType, Msg, Nodes
from . import db
from .create_cluster import create_cluster
from .delete_cluster import delete_cluster
from .healthcheck_cluster import healthcheck_clusters
from .restore_cluster import restore_cluster
from .scale_cluster import scale_cluster
from .upgrade_cluster import upgrade_cluster

logger = logging.getLogger(__name__)


def fail_zombie_jobs():
    db.fail_zombie_jobs()


def get_nodes():

    rs: list[Nodes] = []

    try:
        rs = db.get_nodes()
    except Exception as e:
        print("Error", str(e))

    return [
        {"targets": [f"{n}:8080" for n in x.nodes], "labels": {"cluster": x.cluster_id}}
        for x in rs
    ]


async def pull_from_mq():
    try:
        while True:
            await asyncio.sleep(5 * random.uniform(0.7, 1.3))
            try:
                with db.pool.connection() as conn:
                    with conn.cursor(row_factory=class_row(Msg)) as cur:
                        with conn.transaction():
                            msg = cur.execute(
                                """
                                SELECT * 
                                FROM mq 
                                WHERE now() > start_after 
                                LIMIT 1 
                                FOR UPDATE SKIP LOCKED
                                """
                            ).fetchone()

                            if msg is None:
                                continue

                            logger.info(
                                "Processing MQ message %s of type %s",
                                msg.msg_id,
                                msg.msg_type,
                            )

                            try:
                                match msg.msg_type:
                                    case JobType.CREATE_CLUSTER:
                                        create_cluster(
                                            msg.msg_id, msg.msg_data, msg.created_by
                                        )
                                    case JobType.RECREATE_CLUSTER:
                                        create_cluster(
                                            msg.msg_id,
                                            msg.msg_data,
                                            msg.created_by,
                                            True,
                                        )
                                    case JobType.DELETE_CLUSTER:
                                        delete_cluster(
                                            msg.msg_id, msg.msg_data, msg.created_by
                                        )
                                    case JobType.SCALE_CLUSTER:
                                        scale_cluster(
                                            msg.msg_id, msg.msg_data, msg.created_by
                                        )
                                    case JobType.UPGRADE_CLUSTER:
                                        upgrade_cluster(
                                            msg.msg_id, msg.msg_data, msg.created_by
                                        )
                                    case JobType.RESTORE_CLUSTER:
                                        restore_cluster(
                                            msg.msg_id, msg.msg_data, msg.created_by
                                        )
                                    case JobType.FAIL_ZOMBIE_JOBS:
                                        fail_zombie_jobs()
                                    case JobType.HEALTHCHECK_CLUSTERS:
                                        healthcheck_clusters(msg.msg_id)
                                        cur.execute(
                                            """
                                            INSERT INTO mq (msg_type, start_after) 
                                            VALUES ('HEALTHCHECK_CLUSTERS', now() + INTERVAL '60s' + (random()*10)::INTERVAL)
                                            """
                                        )
                                    case _:
                                        raise ValueError(
                                            f"Unknown task type requested: {msg.msg_type}"
                                        )
                            except Exception as err:
                                logger.exception(
                                    "MQ message %s failed during dispatch",
                                    msg.msg_id,
                                )
                                try:
                                    db.update_job(msg.msg_id, JobState.FAILED)
                                except Exception:
                                    logger.exception(
                                        "Unable to mark job %s as failed",
                                        msg.msg_id,
                                    )
                                try:
                                    db.insert_task(
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
