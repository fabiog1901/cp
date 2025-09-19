import os
from threading import Thread

from .. import db
from ..models import Cluster, ClusterScaleRequest, InventoryLB, InventoryRegion, Region
from .util import MyRunner

PLAYBOOKS_URL = os.getenv("PLAYBOOKS_URL")


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


def scale_cluster(
    job_id: int,
    data: dict,
    requested_by: str,
) -> None:
    cluster_scale_request = ClusterScaleRequest(**data)

    current_cluster = db.get_cluster(cluster_scale_request.name, [], True)

    db.update_cluster(
        cluster_scale_request.name,
        requested_by,
        status="SCALING",
    )

    db.insert_mapped_job(
        cluster_scale_request.name,
        job_id,
        "SCHEDULED",
    )

    Thread(
        target=scale_cluster_worker,
        args=(
            job_id,
            cluster_scale_request,
            current_cluster,
            requested_by,
        ),
    ).start()


def parse_raw_data(regions: list[str], raw_data: dict, current_cluster: Cluster):

    current_cluster.cluster_inventory = []
    current_cluster.lbs_inventory = []

    for cloud_region in regions:
        cloud, region = cloud_region.split(":")

        region_nodes = []

        for i in raw_data["cockroachdb"]:
            if (
                raw_data["hv"][i]["cloud"] == cloud
                and raw_data["hv"][i]["region"] == region
            ):
                region_nodes.append(raw_data["hv"][i]["public_ip"])

        current_cluster.cluster_inventory.append(
            InventoryRegion(cloud=cloud, region=region, nodes=region_nodes)
        )

        for i in raw_data["haproxy"]:
            if (
                raw_data["hv"][i]["cloud"] == cloud
                and raw_data["hv"][i]["region"] == region
            ):
                current_cluster.lbs_inventory.append(
                    InventoryLB(
                        cloud=cloud,
                        region=region,
                        dns_address=raw_data["hv"][i]["public_ip"],
                    )
                )
    return current_cluster


def scale_cluster_worker(
    job_id,
    csr: ClusterScaleRequest,
    current_cluster: Cluster,
    requested_by: str,
):
    deployment = []
    task_id_counter = 0
    current_regions = [
        x.cloud + ":" + x.region for x in current_cluster.cluster_inventory
    ]

    #
    # DISK SIZE
    #
    if csr.disk_size != current_cluster.disk_size:
        extra_vars = {
            "deployment_id": csr.name,
            "disk_size": csr.disk_size,
        }

        job_status, _, task_id_counter = MyRunner(
            job_id,
            task_id_counter,
        ).launch_runner("SCALE_DISK_SIZE", extra_vars)

        if job_status != "successful":
            db.update_cluster(
                csr.name,
                requested_by,
                status="SCALE_FAILED",
            )
            return

        db.update_cluster(
            csr.name,
            requested_by,
            status="SCALING",
            disk_size=csr.disk_size,
        )
        
    #
    # NODE CPUS
    #
    if csr.node_cpus != current_cluster.node_cpus:
        extra_vars = {
            "deployment_id": csr.name,
            "node_cpus": csr.node_cpus,
        }

        job_status, _, task_id_counter = MyRunner(
            job_id,
            task_id_counter,
        ).launch_runner("SCALE_NODE_CPUS", extra_vars)

        if job_status != "successful":
            db.update_cluster(csr.name, requested_by, status="SCALE_FAILED")
            return

        db.update_cluster(
            csr.name,
            requested_by,
            status="SCALING",
            node_cpus=csr.node_cpus
        )
    #
    # NODE COUNT - ADD
    #
    if csr.node_count > current_cluster.node_count:
        deployment = []
        # create new nodes
        for cloud_region in current_regions:
            cloud, region = cloud_region.split(":")

            region_details: list[Region] = db.get_region_details(cloud, region)

            # add 1 HAProxy per region
            deployment.append(
                {
                    "cluster_name": csr.name,
                    "copies": 1,
                    "inventory_groups": ["haproxy"],
                    "exact_count": 1,
                    "instance": {"cpu": 4},
                    "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                    "tags": {"Name": f"{csr.name}-lb"},
                    "groups": [
                        {
                            "user": "ubuntu",
                            "public_ip": True,
                            "public_key_id": "workshop",
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
                len(region_details), csr.node_count
            )

            # add nodes to the deployment
            for idx, zone_count in enumerate(node_count_per_zone):
                deployment.append(
                    {
                        "cluster_name": csr.name,
                        "copies": 1,
                        "inventory_groups": ["cockroachdb"],
                        "exact_count": zone_count,
                        "instance": {"cpu": csr.node_cpus},
                        "volumes": {
                            "os": {"size": 20, "type": "standard_ssd"},
                            "data": [
                                {
                                    "size": csr.disk_size,
                                    "type": "standard_ssd",
                                    "iops": 500 * csr.node_cpus,
                                    "throughput": 30 * csr.node_cpus,
                                    "delete_on_termination": True,
                                }
                            ],
                        },
                        "tags": {"Name": f"{csr.name}-crdb"},
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

        extra_vars = {
            "deployment_id": csr.name,
            "deployment": deployment,
            "current_hosts": [
                x
                for sublist in current_cluster.cluster_inventory
                for x in sublist.nodes
            ],
            "cockroachdb_version": current_cluster.version,
        }

        job_status, raw_data, task_id_counter = MyRunner(
            job_id,
            task_id_counter,
        ).launch_runner("SCALE_CLUSTER_OUT", extra_vars)

        if job_status != "successful":
            db.update_cluster(csr.name, requested_by, status="SCALE_FAILED")
            return

        current_cluster = parse_raw_data(current_regions, raw_data, current_cluster)

        db.update_cluster(
            csr.name,
            requested_by,
            status="SCALING",
            node_count=csr.node_count,
            cluster_inventory=current_cluster.cluster_inventory,
            lbs_inventory=current_cluster.lbs_inventory,
        )

    #
    # NODE COUNT - REMOVE
    #
    if csr.node_count < current_cluster.node_count:
        deployment = []
        # decomm nodes and remove VMs
        for cloud_region in current_regions:
            cloud, region = cloud_region.split(":")

            region_details: list[Region] = db.get_region_details(cloud, region)

            # add 1 HAProxy per region
            deployment.append(
                {
                    "cluster_name": csr.name,
                    "copies": 1,
                    "inventory_groups": ["haproxy"],
                    "exact_count": 1,
                    "instance": {"cpu": 4},
                    "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                    "tags": {"Name": f"{csr.name}-lb"},
                    "groups": [
                        {
                            "user": "ubuntu",
                            "public_ip": True,
                            "public_key_id": "workshop",
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
                len(region_details), csr.node_count
            )

            # add nodes to the deployment
            for idx, zone_count in enumerate(node_count_per_zone):
                deployment.append(
                    {
                        "cluster_name": csr.name,
                        "copies": 1,
                        "inventory_groups": ["cockroachdb"],
                        "exact_count": zone_count,
                        "instance": {"cpu": csr.node_cpus},
                        "volumes": {
                            "os": {"size": 20, "type": "standard_ssd"},
                            "data": [
                                {
                                    "size": csr.disk_size,
                                    "type": "standard_ssd",
                                    "iops": 500 * csr.node_cpus,
                                    "throughput": 30 * csr.node_cpus,
                                    "delete_on_termination": True,
                                }
                            ],
                        },
                        "tags": {"Name": f"{csr.name}-crdb"},
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

        extra_vars = {
            "deployment_id": csr.name,
            "deployment": deployment,
        }

        job_status, raw_data, task_id_counter = MyRunner(
            job_id,
            task_id_counter,
        ).launch_runner("SCALE_CLUSTER_IN", extra_vars)

        if job_status != "successful":
            db.update_cluster(csr.name, requested_by, status="SCALE_FAILED")
            return

        current_cluster = parse_raw_data(current_regions, raw_data, current_cluster)

        db.update_cluster(
            csr.name,
            requested_by,
            node_count=csr.node_count,
            status="SCALING",
            cluster_inventory=current_cluster.cluster_inventory,
            lbs_inventory=current_cluster.lbs_inventory,
        )

    #
    # REGIONS - ADD
    #

    # new regions: check if there are any region in the request that's not in the current regions
    new_regions = [x for x in csr.regions if x not in current_regions]

    if new_regions:
        deployment = []
        for cloud_region in current_regions + new_regions:
            cloud, region = cloud_region.split(":")

            region_details: list[Region] = db.get_region_details(cloud, region)

            # add 1 HAProxy per region
            deployment.append(
                {
                    "cluster_name": csr.name,
                    "copies": 1,
                    "inventory_groups": ["haproxy"],
                    "exact_count": 1,
                    "instance": {"cpu": 4},
                    "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                    "tags": {"Name": f"{csr.name}-lb"},
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
                len(region_details), csr.node_count
            )

            # add nodes to the deployment
            for idx, zone_count in enumerate(node_count_per_zone):
                deployment.append(
                    {
                        "cluster_name": csr.name,
                        "copies": 1,
                        "inventory_groups": ["cockroachdb"],
                        "exact_count": zone_count,
                        "instance": {"cpu": csr.node_cpus},
                        "volumes": {
                            "os": {"size": 20, "type": "standard_ssd"},
                            "data": [
                                {
                                    "size": csr.disk_size,
                                    "type": "standard_ssd",
                                    "iops": 500 * csr.node_cpus,
                                    "throughput": 30 * csr.node_cpus,
                                    "delete_on_termination": True,
                                }
                            ],
                        },
                        "tags": {"Name": f"{csr.name}-crdb"},
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

        extra_vars = {
            "deployment_id": csr.name,
            "deployment": deployment,
            "current_hosts": [
                x
                for sublist in current_cluster.cluster_inventory
                for x in sublist.nodes
            ],
            "cockroachdb_version": current_cluster.version,
        }

        job_status, raw_data, task_id_counter = MyRunner(
            job_id,
            task_id_counter,
        ).launch_runner("SCALE_CLUSTER_OUT", extra_vars)

        if job_status != "successful":
            db.update_cluster(csr.name, requested_by, status="SCALE_FAILED")
            return

        current_cluster = parse_raw_data(csr.regions, raw_data, current_cluster)

        db.update_cluster(
            csr.name,
            requested_by,
            status="SCALING",
            cluster_inventory=current_cluster.cluster_inventory,
            lbs_inventory=current_cluster.lbs_inventory,
        )

    #
    # REGION - REMOVE
    #

    # remove region: check for any region that's in the current list that's no longer in the request
    remove_regions = [x for x in current_regions if x not in csr.regions]

    if remove_regions:
        # decomm region nodes
        deployment = []
        # decomm nodes and remove VMs
        for cloud_region in csr.regions:
            cloud, region = cloud_region.split(":")

            region_details: list[Region] = db.get_region_details(cloud, region)

            # add 1 HAProxy per region
            deployment.append(
                {
                    "cluster_name": csr.name,
                    "copies": 1,
                    "inventory_groups": ["haproxy"],
                    "exact_count": 1,
                    "instance": {"cpu": 4},
                    "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                    "tags": {"Name": f"{csr.name}-lb"},
                    "groups": [
                        {
                            "user": "ubuntu",
                            "public_ip": True,
                            "public_key_id": "workshop",
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
                len(region_details), csr.node_count
            )

            # add nodes to the deployment
            for idx, zone_count in enumerate(node_count_per_zone):
                deployment.append(
                    {
                        "cluster_name": csr.name,
                        "copies": 1,
                        "inventory_groups": ["cockroachdb"],
                        "exact_count": zone_count,
                        "instance": {"cpu": csr.node_cpus},
                        "volumes": {
                            "os": {"size": 20, "type": "standard_ssd"},
                            "data": [
                                {
                                    "size": csr.disk_size,
                                    "type": "standard_ssd",
                                    "iops": 500 * csr.node_cpus,
                                    "throughput": 30 * csr.node_cpus,
                                    "delete_on_termination": True,
                                }
                            ],
                        },
                        "tags": {"Name": f"{csr.name}-crdb"},
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

        extra_vars = {
            "deployment_id": csr.name,
            "deployment": deployment,
        }

        job_status, raw_data, task_id_counter = MyRunner(
            job_id,
            task_id_counter,
        ).launch_runner("SCALE_CLUSTER_IN", extra_vars)

        if job_status != "successful":
            db.update_cluster(
                csr.name,
                requested_by,
                status="SCALE_FAILED",
            )
            return

        current_cluster = parse_raw_data(csr.regions, raw_data, current_cluster)

        db.update_cluster(
            csr.name,
            requested_by,
            status="SCALING",
            cluster_inventory=current_cluster.cluster_inventory,
            lbs_inventory=current_cluster.lbs_inventory,
        )

    db.update_cluster(
        csr.name,
        requested_by,
        status="RUNNING",
    )
