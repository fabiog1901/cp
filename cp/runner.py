import threading
import time
import datetime as dt

from . import db


def create_cluster(
    job_id: int,
    cluster: dict,
) -> None:
    c = db.get_cluster(cluster["cluster_id"])
    if c:
        # TODO raise an error message that a cluster
        # with the same name already exists
        db.create_job(
            job_id,
            "CREATE_CLUSTER",
            "FAILED",
            "root",
        )
        return

    db.create_cluster(
        cluster["cluster_id"],
        "PROVISIONING",
        "root",
        "root",
    )

    db.create_job_linked(
        cluster["cluster_id"],
        job_id,
        "CREATE_CLUSTER",
        "STARTED",
        "root",
    )

    threading.Thread(
        target=create_cluster_worker,
        args=(
            job_id,
            cluster,
        ),
    ).start()


def create_cluster_worker(job_id, cluster):
    for x in range(15):
        # actually doing some real work
        time.sleep(5)

        # the ansible playbook outputs task events
        db.create_task(
            job_id,
            x,
            x * 100 // 15,
            dt.datetime.now(),
            f"event_{x}",
            {"k": "v"},
        )

    db.update_job(job_id, "COMPLETED")
    db.update_cluster(
        cluster["cluster_id"],
        "OK",
        {"lbs": ["10.10.15.48", "10.10.68.175"]},
        "root",
    )
