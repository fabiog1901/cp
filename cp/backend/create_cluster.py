from threading import Thread

from ..models import (
    ClusterRequest,
    ClusterState,
    InventoryLB,
    InventoryRegion,
    JobState,
    Region,
)
from . import db
from .util import MyRunner


def get_node_count_per_zone(zone_count: int, node_count: int) -> list[int]:
    # make a list with the same size as the count of zones
    # zone = 3, nodes = 8 ==> [3, 3, 2]

    l = [0] * zone_count
    i = 0

    # distribute node to each zone
    for _ in range(node_count):
        l[i] += 1
        i += 1
        if i == zone_count:
            i = 0

    return l


def create_cluster(
    job_id: int,
    data: dict,
    created_by: str,
    recreate: bool = False,
) -> None:
    cluster_request = ClusterRequest(**data)

    # check if cluster with same cluster_id exists
    c = db.get_cluster(cluster_request.name, [], True)

    if not recreate and c and c.status.startswith("DELET"):
        # TODO raise an error message that a cluster
        # with the same name already exists
        db.update_job(
            job_id,
            JobState.FAILED,
        )
        return

    db.upsert_cluster(
        cluster_request.name,
        ClusterState.PROVISIONING,
        created_by,
        cluster_request.group,
        cluster_request.version,
        cluster_request.node_cpus,
        cluster_request.node_count,
        cluster_request.disk_size,
    )

    db.insert_mapped_job(
        cluster_request.name,
        job_id,
        JobState.SCHEDULED,
    )

    Thread(
        target=create_cluster_worker,
        args=(
            job_id,
            cluster_request,
            created_by,
        ),
    ).start()


def create_cluster_worker(job_id, cluster_request: ClusterRequest, created_by: str):
    deployment = []

    for cloud_region in cluster_request.regions:
        cloud, region = cloud_region.split(":")

        region_details: list[Region] = db.get_region_details(cloud, region)

        # add 1 HAProxy per region
        deployment.append(
            {
                "cluster_name": cluster_request.name,
                "copies": 1,
                "inventory_groups": ["haproxy"],
                "exact_count": 1,
                "instance": {"cpu": 4},
                "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                "tags": {"Name": f"{cluster_request.name}-lb"},
                "groups": [
                    {
                        "user": "ubuntu",
                        "public_ip": True,
                        "public_key_id": "workshop",
                        "tags": {"owner": "fabio"},
                        "cloud": cloud,
                        "image": region_details[0].image,
                        "region": region,
                        "vpc_id": region_details[0].vpc_id,
                        "security_groups": region_details[0].security_groups,
                        "zone": region_details[0].zone,
                        "subnet": region_details[0].subnet,
                    }
                ],
            }
            | region_details[0].extras
        )

        # distribute the node_counts over all available zones

        node_count_per_zone = get_node_count_per_zone(
            len(region_details), cluster_request.node_count
        )

        for idx, zone_count in enumerate(node_count_per_zone):
            deployment.append(
                {
                    "cluster_name": cluster_request.name,
                    "copies": 1,
                    "inventory_groups": ["cockroachdb"],
                    "exact_count": zone_count,
                    "instance": {"cpu": cluster_request.node_cpus},
                    "volumes": {
                        "os": {"size": 20, "type": "standard_ssd"},
                        "data": [
                            {
                                "size": cluster_request.disk_size,
                                "type": "standard_ssd",
                                "iops": 500 * cluster_request.node_cpus,
                                "throughput": 30 * cluster_request.node_cpus,
                                "delete_on_termination": True,
                            }
                        ],
                    },
                    "tags": {"Name": f"{cluster_request.name}-crdb"},
                    "groups": [
                        {
                            "user": "ubuntu",
                            "public_ip": True,
                            "public_key_id": "workshop",
                            "tags": {"owner": "fabio"},
                            "cloud": cloud,
                            "image": region_details[idx].image,
                            "region": region,
                            "vpc_id": region_details[idx].vpc_id,
                            "security_groups": region_details[idx].security_groups,
                            "zone": region_details[idx].zone,
                            "subnet": region_details[idx].subnet,
                        }
                    ],
                }
                | region_details[idx].extras
            )

    # TODO get all these details from Settings instad of hardcoded values
    extra_vars = {
        "deployment_id": cluster_request.name,
        "deployment": deployment,
        "cockroachdb_version": cluster_request.version,
        "cockroachdb_cluster_organization": db.get_setting("licence_org"),
        "cockroachdb_enterprise_license": db.get_setting("licence_key"),
        "dbusers": [
            {
                "name": db.get_setting("default_username"),
                "password": db.get_setting("default_password"),
                "is_cert": False,
                "is_admin": True,
            }
        ],
        "cloud_storage_url": db.get_setting("cloud_storage_url"),
    }

    job_status, raw_data, _ = MyRunner(job_id).launch_runner(
        "CREATE_CLUSTER", extra_vars
    )

    cluster_inventory: list[InventoryRegion] = []
    lbs_inventory: list[InventoryLB] = []

    if job_status != "successful":
        db.update_cluster(cluster_request.name, created_by, status=ClusterState.FAILED)
        return

    for cloud_region in cluster_request.regions:
        cloud, region = cloud_region.split(":")

        region_nodes = []

        for x in raw_data["cockroachdb"]:
            if x["cloud"] == cloud and x["region"] == region:
                region_nodes.append(x["public_ip"])

        cluster_inventory.append(
            InventoryRegion(cloud=cloud, region=region, nodes=region_nodes)
        )

        for x in raw_data["haproxy"]:
            if x["cloud"] == cloud and x["region"] == region:
                lbs_inventory.append(
                    InventoryLB(
                        cloud=cloud,
                        region=region,
                        dns_address=x["public_ip"],
                    )
                )

    db.update_cluster(
        cluster_request.name,
        created_by,
        status=ClusterState.RUNNING,
        cluster_inventory=cluster_inventory,
        lbs_inventory=lbs_inventory,
    )
