import threading
from uuid import uuid4
import time
from . import db
import datetime as dt


def create_cluster(
    cluster: dict,
) -> None:
    # create a new thread to run the create_cluster function

    job_id = uuid4()
    db.create_job(
        cluster["cluster_id"],
        job_id,
        "CREATE_CLUSTER",
        "STARTED",
        "root",
    )

    threading.Thread(
        target=create_cluster_runner,
        args=(
            job_id,
            cluster,
        ),
    ).start()

    return job_id


def create_cluster_runner(job_id, cluster):
    for x in range(10):
        # actually doing some real work
        time.sleep(5)

        # the ansible playbook outputs task events
        db.create_task(
            cluster["cluster_id"],
            job_id,
            x,
            x * 100 // 120,
            dt.datetime.now(),
            f"event_{x}",
            {"k": "v"},
        )

    db.update_job(cluster["cluster_id"], job_id, "COMPLETED")
    db.update_cluster(cluster["cluster_id"], "OK", {}, "root")
