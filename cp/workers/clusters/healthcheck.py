import os
from threading import Thread

from ...infra import get_repo
from ...models import ClusterState, JobType
from ..ansible import MyRunnerLite


def healthcheck_clusters(job_id: int) -> None:
    repo = get_repo()
    running_clusters = repo.get_running_clusters()

    for cluster in running_clusters:
        ssh_key_name = cluster.description["ssh_key"]

        if not os.path.exists(f"/tmp/{ssh_key_name}"):
            ssh_key = repo.get_secret(ssh_key_name)

            with open(f"/tmp/{ssh_key_name}", "w") as f:
                f.write(ssh_key)

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
    repo = get_repo()
    extra_vars = {
        "deployment_id": cluster_id,
        "cockroachdb_nodes": cockroachdb_nodes,
        "ssh_key": ssh_key,
    }

    job_status, data = MyRunnerLite(job_id).launch_runner(
        JobType.HEALTHCHECK_CLUSTERS, extra_vars
    )

    if not data or job_status != "successful":
        repo.update_cluster(
            cluster_id,
            "system",
            status=ClusterState.UNHEALTHY,
        )

    for node in data.get("data", []):
        if node["is_live"] == "false":
            repo.update_cluster(
                cluster_id,
                "system",
                status=ClusterState.UNHEALTHY,
            )
