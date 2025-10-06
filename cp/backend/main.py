import asyncio
import random

from psycopg.rows import class_row

from .. import db
from ..models import JobType, Msg
from .create_cluster import create_cluster
from .delete_cluster import delete_cluster
from .healthcheck_cluster import healthcheck_clusters
from .restore_cluster import restore_cluster
from .scale_cluster import scale_cluster
from .upgrade_cluster import upgrade_cluster


def fail_zombie_jobs():
    db.fail_zombie_jobs()


async def pull_from_mq():
    try:
        while True:
            # add some polling delay to avoid running too often
            await asyncio.sleep(5 * random.uniform(0.7, 1.3))

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

                        print(f"Processing a {msg.msg_type}")

                        match msg.msg_type:
                            case JobType.CREATE_CLUSTER:
                                create_cluster(msg.msg_id, msg.msg_data, msg.created_by)

                            case JobType.RECREATE_CLUSTER:
                                create_cluster(
                                    msg.msg_id, msg.msg_data, msg.created_by, True
                                )
                            case JobType.DELETE_CLUSTER:
                                delete_cluster(msg.msg_id, msg.msg_data, msg.created_by)

                            case JobType.SCALE_CLUSTER:
                                scale_cluster(msg.msg_id, msg.msg_data, msg.created_by)

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
                                print(f"Unknown task type requested: {msg.msg_type}")

                        cur.execute(
                            "DELETE FROM mq WHERE msg_id = %s;",
                            (msg.msg_id,),
                        )

    except asyncio.CancelledError:
        print("Task pull_from_mq was stopped")
