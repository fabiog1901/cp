import asyncio
import os
import random
from threading import Thread

from psycopg.rows import class_row

from .. import db
from ..models import Msg
from .create_cluster import create_cluster
from .delete_cluster import delete_cluster
from .scale_cluster import scale_cluster
from .upgrade_cluster import upgrade_cluster
from .util import MyRunnerLite

PLAYBOOKS_URL = os.getenv("PLAYBOOKS_URL")


def fail_zombie_jobs():
    db.fail_zombie_jobs()


def healthcheck_clusters(job_id: int) -> None:
    running_clusters = db.get_running_clusters()

    for cluster in running_clusters:
        ssh_key_name = cluster.description["ssh_key"]

        if not os.path.exists(f"/tmp/{ssh_key_name}"):
            ssh_key = db.get_secret(ssh_key_name)

            with open(f"/tmp/{ssh_key_name}", "w") as f:
                f.write(ssh_key.id)

        cockroachdb_nodes = []
        for region in cluster.description["cluster"]:
            cockroachdb_nodes += region["nodes"]

        Thread(
            target=healthcheck_clusters_worker,
            args=(
                job_id,
                cluster.cluster_id,
                cockroachdb_nodes,
                f"/tmp/{ssh_key_name}",
            ),
        ).start()


def healthcheck_clusters_worker(
    job_id: int,
    cluster_id: str,
    cockroachdb_nodes: list[str],
    ssh_key: str,
):
    extra_vars = {
        "deployment_id": cluster_id,
        "cockroachdb_nodes": cockroachdb_nodes,
        "ssh_key": ssh_key,
    }

    job_status, data, _ = MyRunnerLite().launch_runner(
        "HEALTHCHECK_CLUSTERS", extra_vars
    )

    if not data or job_status != "successful":
        db.update_cluster(
            cluster_id,
            "system",
            status="UNHEALTHY",
        )

    for node in data.get("data", []):
        if node["is_live"] == "false":
            db.update_cluster(
                cluster_id,
                "system",
                status="UNHEALTHY",
            )


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
                            case "CREATE_CLUSTER":
                                create_cluster(msg.msg_id, msg.msg_data, msg.created_by)

                            case "RECREATE_CLUSTER":
                                create_cluster(
                                    msg.msg_id, msg.msg_data, msg.created_by, True
                                )
                            case "DELETE_CLUSTER":
                                delete_cluster(msg.msg_id, msg.msg_data, msg.created_by
                                               
                                               )

                            case "SCALE_CLUSTER":
                                scale_cluster(msg.msg_id, msg.msg_data, msg.created_by)

                            case "UPGRADE_CLUSTER":
                                upgrade_cluster(
                                    msg.msg_id, msg.msg_data, msg.created_by
                                )

                            case "FAIL_ZOMBIE_JOBS":
                                fail_zombie_jobs()

                            case "HEALTHCHECK_CLUSTERS":
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
        print("Task was stopped")
