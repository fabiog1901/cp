import os
from threading import Thread

from .. import db
from ..models import ClusterState, JobType
from .util import MyRunnerLite


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
        JobType.HEALTHCHECK_CLUSTERS, extra_vars
    )

    if not data or job_status != "successful":
        db.update_cluster(
            cluster_id,
            "system",
            status=ClusterState.UNHEALTHY,
        )

    for node in data.get("data", []):
        if node["is_live"] == "false":
            db.update_cluster(
                cluster_id,
                "system",
                status=ClusterState.UNHEALTHY,
            )
