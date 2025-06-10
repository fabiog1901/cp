import asyncio
import json
import os
import shutil
import random
import time
from threading import Thread

import ansible_runner
import requests
from pprint import pprint

from . import db
from .models import ClusterRequest, Msg, Region, ClusterScaleRequest
import os

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


def create_cluster(
    job_id: int,
    cluster: dict,
    created_by: str,
    recreate: bool = False,
) -> None:
    cluster_request = ClusterRequest(**cluster)

    # check if cluster with same cluster_id exists
    c = db.get_cluster(cluster_request.name, [], True)

    if not recreate and c and c.status == "DELETED":
        # TODO raise an error message that a cluster
        # with the same name already exists
        db.update_job(
            job_id,
            "FAILED",
        )
        return

    db.upsert_cluster(
        cluster_request.name,
        "PROVISIONING",
        {"cluster": [], "lbs": [], "disk_size": 0, "node_cpus": 0, "version": ""},
        created_by,
        created_by,
        cluster["group"],
    )

    db.insert_mapped_job(
        cluster_request.name,
        job_id,
        "SCHEDULED",
    )

    Thread(
        target=create_cluster_worker,
        args=(
            job_id,
            cluster_request,
        ),
    ).start()


def create_cluster_worker(job_id, cluster_request: ClusterRequest):
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

    extra_vars = {
        "deployment_id": cluster_request.name,
        "deployment": deployment,
        "cockroachdb_version": cluster_request.version,
        "cockroachdb_cluster_organization": "Workshop",
        "cockroachdb_enterprise_license": "crl-0-EIq0kMMGGAIiCFdvcmtzaG9w",
        "dbusers": [
            {
                "name": "cockroach",
                "password": "cockroach",
                "is_cert": False,
                "is_admin": True,
            }
        ],
    }

    job_status, raw_data = MyRunner(job_id).launch_runner("CREATE_CLUSTER", extra_vars)

    data = {
        "version": cluster_request.version,
        "node_cpus": cluster_request.node_cpus,
        "disk_size": cluster_request.disk_size,
        "cluster": [],
        "lbs": [],
    }

    if job_status != "successful":
        db.update_cluster(
            cluster_request.name,
            "FAILED",
            {},
            "root",
        )
        return

    for cloud_region in cluster_request.regions:
        cloud, region = cloud_region.split(":")

        region_nodes = []

        for i in raw_data["cockroachdb"]:
            if (
                raw_data["hv"][i]["cloud"] == cloud
                and raw_data["hv"][i]["region"] == region
            ):
                region_nodes.append(raw_data["hv"][i]["public_ip"])

        data["cluster"].append(
            {
                "cloud": cloud,
                "region": region,
                "nodes": region_nodes,
            }
        )

        for i in raw_data["haproxy"]:
            if (
                raw_data["hv"][i]["cloud"] == cloud
                and raw_data["hv"][i]["region"] == region
            ):
                data["lbs"].append(
                    {
                        "cloud": cloud,
                        "region": region,
                        "dns_address": raw_data["hv"][i]["public_ip"],
                    }
                )

    db.update_cluster(
        cluster_request.name,
        "RUNNING",
        data,
        "system",
    )


def delete_cluster(
    job_id: int,
    cluster: dict,
) -> None:
    cluster_id = cluster.get("cluster_id")

    c = db.get_cluster(cluster_id, [], True)
    if not c or c.status == "DELETED":
        # TODO if cluster doesn't exists or it's already marked as deleted,
        # fail the job
        db.update_job(
            job_id,
            "FAILED",
        )
        return

    db.update_cluster_status(
        cluster_id,
        "DELETING...",
        "system",
    )

    db.insert_mapped_job(
        cluster_id,
        job_id,
        "SCHEDULED",
    )

    Thread(
        target=delete_cluster_worker,
        args=(
            job_id,
            cluster_id,
        ),
    ).start()


def delete_cluster_worker(job_id: int, cluster_id: str):
    extra_vars = {
        "deployment_id": cluster_id,
    }

    job_status, data = MyRunner(job_id).launch_runner("DELETE_CLUSTER", extra_vars)

    if job_status == "successful":
        db.update_cluster_status(
            cluster_id,
            "DELETED",
            "system",
        )
    else:
        db.update_cluster_status(
            cluster_id,
            "DELETE_FAILED",
            "system",
        )


def scale_cluster(
    job_id: int,
    cluster: dict,
    created_by: str,
) -> None:
    cluster_scale_request = ClusterScaleRequest(**cluster)

    print("cluster scale request")
    pprint(cluster_scale_request)
    print()

    c = db.get_cluster(cluster_scale_request.name, [], True)

    db.update_cluster_status(
        cluster_scale_request.name,
        "SCALING",
        created_by,
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
            c.description,
        ),
    ).start()


def scale_cluster_worker(
    job_id,
    cluster_scale_request: ClusterScaleRequest,
    current_desc: dict,
):
    deployment = []
    current_regions = [x["cloud"] + ":" + x["region"] for x in current_desc["cluster"]]

    #
    # DISK SIZE
    #
    if cluster_scale_request.disk_size != current_desc["disk_size"]:
        extra_vars = {
            "deployment_id": cluster_scale_request.name,
            "disk_size": cluster_scale_request.disk_size,
        }

        job_status, data = MyRunner(job_id).launch_runner("SCALE_DISK_SIZE", extra_vars)

        if job_status != "successful":
            db.update_cluster_status(
                cluster_scale_request.name,
                "SCALE_FAILED",
                "system",
            )
            return

    #
    # NODE CPUS
    #
    if cluster_scale_request.node_cpus != current_desc["node_cpus"]:
        extra_vars = {
            "deployment_id": cluster_scale_request.name,
            "node_cpus": cluster_scale_request.node_cpus,
        }

        job_status, data = MyRunner(job_id).launch_runner("SCALE_NODE_CPUS", extra_vars)

        if job_status != "successful":
            db.update_cluster_status(
                cluster_scale_request.name,
                "SCALE_FAILED",
                "system",
            )
            return

    #
    # NODE COUNT
    #

    # add nodes
    if cluster_scale_request.node_count > len(current_desc["cluster"][0]["nodes"]):
        # create new nodes
        for cloud_region in current_regions:
            cloud, region = cloud_region.split(":")

            region_details: list[Region] = db.get_region_details(cloud, region)

            # add 1 HAProxy per region
            deployment.append(
                {
                    "cluster_name": cluster_scale_request.name,
                    "copies": 1,
                    "inventory_groups": ["haproxy"],
                    "exact_count": 1,
                    "instance": {"cpu": 4},
                    "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                    "tags": {"Name": f"{cluster_scale_request.name}-lb"}
                    | region_details[0].tags,
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
                len(region_details), cluster_scale_request.node_count
            )

            # add nodes to the deployment
            for idx, zone_count in enumerate(node_count_per_zone):
                deployment.append(
                    {
                        "cluster_name": cluster_scale_request.name,
                        "copies": 1,
                        "inventory_groups": ["cockroachdb"],
                        "exact_count": zone_count,
                        "instance": {"cpu": cluster_scale_request.node_cpus},
                        "volumes": {
                            "os": {"size": 20, "type": "standard_ssd"},
                            "data": [
                                {
                                    "size": cluster_scale_request.disk_size,
                                    "type": "standard_ssd",
                                    "iops": 500 * cluster_scale_request.node_cpus,
                                    "throughput": 30 * cluster_scale_request.node_cpus,
                                    "delete_on_termination": True,
                                }
                            ],
                        },
                        "tags": {"Name": f"{cluster_scale_request.name}-crdb"},
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
            "deployment_id": cluster_scale_request.name,
            "deployment": deployment,
            "current_hosts": [
                x for sublist in current_desc["cluster"] for x in sublist["nodes"]
            ],
            "cockroachdb_version": current_desc["version"],
        }
        
    
        job_status, raw_data = MyRunner(job_id).launch_runner(
            "SCALE_CLUSTER", extra_vars
        )

        if job_status != "successful":
            db.update_cluster_status(
                cluster_scale_request.name,
                "SCALE_FAILED",
                "root",
            )
            return

    # remove nodes
    if cluster_scale_request.node_count < len(current_desc["cluster"][0]["nodes"]):
        pass  # decomm nodes

    #
    # NEW REGIONS
    #

    # new regions: check if there are any region in the request that's not in the current regions
    new_regions = [x for x in cluster_scale_request.regions if x not in current_regions]

    if new_regions:
        for cloud_region in current_regions + new_regions:
            cloud, region = cloud_region.split(":")

            region_details: list[Region] = db.get_region_details(cloud, region)

            # add 1 HAProxy per region
            deployment.append(
                {
                    "cluster_name": cluster_scale_request.name,
                    "copies": 1,
                    "inventory_groups": ["haproxy"],
                    "exact_count": 1,
                    "instance": {"cpu": 4},
                    "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                    "tags": {"Name": f"{cluster_scale_request.name}-lb"},
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
                len(region_details), cluster_scale_request.node_count
            )

            # add nodes to the deployment
            for idx, zone_count in enumerate(node_count_per_zone):
                deployment.append(
                    {
                        "cluster_name": cluster_scale_request.name,
                        "copies": 1,
                        "inventory_groups": ["cockroachdb"],
                        "exact_count": zone_count,
                        "instance": {"cpu": cluster_scale_request.node_cpus},
                        "volumes": {
                            "os": {"size": 20, "type": "standard_ssd"},
                            "data": [
                                {
                                    "size": cluster_scale_request.disk_size,
                                    "type": "standard_ssd",
                                    "iops": 500 * cluster_scale_request.node_cpus,
                                    "throughput": 30 * cluster_scale_request.node_cpus,
                                    "delete_on_termination": True,
                                }
                            ],
                        },
                        "tags": {"Name": f"{cluster_scale_request.name}-crdb"},
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
            "state": "present",
            "owner": "fabio",
            "deployment_id": cluster_scale_request.name,
            "deployment": deployment,
            "certificates_organization_name": "{{ owner }}-org",
            "certificates_dir": "certs",
            "certificates_usernames": ["root"],
            # "certificates_hosts": "{{ groups['cockroachdb'] }}",
            "certificates_loadbalancer": "{{ groups['haproxy'] | default('') }}",
            "cockroachdb_deployment": "standard",
            "cockroachdb_secure": True,
            "cockroachdb_certificates_dir": "certs",
            "cockroachdb_certificates_clients": ["root"],
            # "cockroachdb_version": cluster_request.version,
            "cockroachdb_join": [
                "{{ hostvars[( groups[cluster_name] | intersect(groups['cockroachdb']) )[0]].public_ip }}",
                "{{ hostvars[( groups[cluster_name] | intersect(groups['cockroachdb']) )[1]].public_ip }}",
                "{{ hostvars[( groups[cluster_name] | intersect(groups['cockroachdb']) )[2]].public_ip }}",
            ],
            "cockroachdb_sql_port": 26257,
            "cockroachdb_rpc_port": 26357,
            "cockroachdb_http_addr_ip": "0.0.0.0",
            "cockroachdb_http_addr_port": "8080",
            "cockroachdb_cache": ".35",
            "cockroachdb_max_sql_memory": ".35",
            "cockroachdb_max_offset": "250ms",
            "cockroachdb_upgrade_delay": 60,
            "cockroachdb_locality": "cloud={{ cloud | default('') }},region={{ region | default('') }},zone={{ zone | default('') }}",
            "cockroachdb_advertise_addr": "{{ public_ip | default('') }}",
            "cockroachdb_cluster_organization": "Workshop",
            "cockroachdb_enterprise_license": "crl-0-EJPvvcEGGAIiCFdvcmtzaG9w",
            "cockroachdb_encryption": False,
            "cockroachdb_autofinalize": True,
            "cockroachdb_env_vars": ["KRB5_KTNAME=/var/lib/cockroach/cockroach.keytab"],
            "dbusers": [
                {
                    "name": "cockroach",
                    "password": "cockroach",
                    "is_cert": False,
                    "is_admin": True,
                }
            ],
        }
        
        extra_vars = {
            "deployment_id": cluster_scale_request.name,
            "deployment": deployment,
            "current_hosts": [
                x for sublist in current_desc["cluster"] for x in sublist["nodes"]
            ],
            "cockroachdb_version": current_desc["version"],
        }

        job_status, raw_data = MyRunner(job_id).launch_runner(
            "SCALE_CLUSTER", extra_vars
        )

        if job_status != "successful":
            db.update_cluster_status(
                cluster_scale_request.name,
                "SCALE_FAILED",
                "root",
            )
            return

    # remove region: check for any region that's in the current list that's no longer in the request
    remove_regions = [
        x for x in current_regions if x not in cluster_scale_request.regions
    ]
    if remove_regions:
        # decomm region nodes
        pass

    data = {
        "version": current_desc["version"],
        "node_cpus": cluster_scale_request.node_cpus,
        "disk_size": cluster_scale_request.disk_size,
        "cluster": [],
        "lbs": [],
    }

    if job_status != "successful":
        db.update_cluster_status(
            cluster_scale_request.name,
            "FAILED",
            "root",
        )
        return

    for cloud_region in cluster_scale_request.regions:
        cloud, region = cloud_region.split(":")

        region_nodes = []

        for i in raw_data["cockroachdb"]:
            if (
                raw_data["hv"][i]["cloud"] == cloud
                and raw_data["hv"][i]["region"] == region
            ):
                region_nodes.append(raw_data["hv"][i]["public_ip"])

        data["cluster"].append(
            {
                "cloud": cloud,
                "region": region,
                "nodes": region_nodes,
            }
        )

        for i in raw_data["haproxy"]:
            if (
                raw_data["hv"][i]["cloud"] == cloud
                and raw_data["hv"][i]["region"] == region
            ):
                data["lbs"].append(
                    {
                        "cloud": cloud,
                        "region": region,
                        "dns_address": raw_data["hv"][i]["public_ip"],
                    }
                )

    db.update_cluster(
        cluster_scale_request.name,
        "RUNNING",
        data,
        "system",
    )


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

    job_status, data = MyRunnerLite().launch_runner("HEALTHCHECK_CLUSTERS", extra_vars)

    if not data or job_status != "successful":
        db.update_cluster_status(
            cluster_id,
            "UNHEALTHY",
            "system",
        )

    for node in data.get("data", []):
        if node["is_live"] == "false":
            db.update_cluster_status(
                cluster_id,
                "UNHEALTHY",
                "system",
            )


class MyRunner:
    def __init__(self, job_id: int):
        self.data = {}
        self.job_id = job_id

    def my_status_handler(self, status, runner_config):
        return

    def my_event_handler(self, e):
        task_type = ""
        task_data = ""

        if e["event"] in [
            "verbose",
            "playbook_on_start",
            "playbook_on_no_hosts_matched",
            "runner_on_skipped",
            "runner_item_on_skipped",
            "runner_item_on_ok",
            "runner_on_start",
            "playbook_on_include",
        ]:
            return

        elif e["event"] == "runner_on_ok":
            if e.get("event_data")["task"] == "Data":
                self.data = e["event_data"]["res"]["msg"]
            return

        elif e["event"] == "warning":
            task_type = "WARNING"
            task_data = e["stdout"]

        elif e["event"] == "error":
            task_type = "ERROR"
            task_data = e["stdout"]

        elif e["event"] == "playbook_on_play_start":
            task_type = f"PLAY [{e['event_data']['play']}]"

        elif e["event"] == "playbook_on_task_start":
            task_type = f"{e['event_data']['task']}"

        elif e["event"] == "runner_on_failed":
            task_data = f"fatal: [{e['event_data']['host']}]\n{json.dumps(e['event_data']['res']['msg'])}"

        elif e["event"] == "runner_item_on_failed":
            task_data = f"fatal: [{e['event_data']['host']}]\n{e['event_data']['res']['stderr']}"

        elif e["event"] == "playbook_on_stats":
            task_type = "PLAY RECAP"
            task_data = (
                f"ok: {e['event_data']['ok']} \nfailures: {e['event_data']['failures']}"
            )

        else:
            # new event not being catched
            task_type = e["event"]
            task_data = json.dumps(e)

        db.insert_task(
            self.job_id,
            e["counter"],
            e["created"],
            task_type,
            task_data,
        )

    def launch_runner(self, playbook_name: str, extra_vars: dict) -> tuple[str, dict]:
        # fetch all plays for a playbook
        r = requests.get(PLAYBOOKS_URL + playbook_name + ".yaml")

        # create a new working directory
        shutil.rmtree(f"/tmp/job-{self.job_id}", ignore_errors=True)
        os.mkdir(path=f"/tmp/job-{self.job_id}")
        
        with open(f"/tmp/job-{self.job_id}/playbook.yaml", "wb") as f:
            f.write(r.content)

        db.update_job(self.job_id, "RUNNING")

        # Execute the playbook
        try:
            thread, runner = ansible_runner.run_async(
                quiet=False,
                verbosity=1,
                playbook=f"/tmp/job-{self.job_id}/playbook.yaml", 
                private_data_dir=f"/tmp/job-{self.job_id}",
                extravars=extra_vars,
                event_handler=self.my_event_handler,
                status_handler=self.my_status_handler,
            )
        except Exception as e:
            db.update_job(self.job_id, "FAILED")
            print(f"Error running playbook: {e}")

        heartbeat_ts = time.time() + 60
        while thread.is_alive():
            # send hb messsage periodically
            if time.time() > heartbeat_ts:
                db.update_job(self.job_id, "RUNNING")
                heartbeat_ts = time.time() + 60

            time.sleep(1)

        # update the Job status
        if runner.status == "successful":
            db.update_job(self.job_id, "COMPLETED")
        else:
            db.update_job(self.job_id, "FAILED")

        # rm -rf job-directory
        shutil.rmtree(f"/tmp/job-{self.job_id}", ignore_errors=True)

        return runner.status, self.data


class MyRunnerLite:
    def __init__(self):
        self.data = {}

    def my_status_handler(self, status, runner_config):
        return

    def my_event_handler(self, e):
        if e["event"] == "runner_on_ok":
            if e.get("event_data")["task"] == "Data":
                self.data = e["event_data"]["res"]["msg"]

    def launch_runner(self, playbook_name: str, extra_vars: dict) -> tuple[str, dict]:
        # fetch the playbook if it doesn't exists locally or
        # it's older than 24h
        if (
            not os.path.exists(f"/tmp/{playbook_name}.yaml")
            or os.path.getmtime(f"/tmp/{playbook_name}.yaml") + 86400 < time.time()
        ):
            r = requests.get(PLAYBOOKS_URL + playbook_name + ".yaml")

            with open(f"/tmp/{playbook_name}.yaml", "wb") as f:
                f.write(r.content)

        # Execute the playbook
        try:
            thread, runner = ansible_runner.run_async(
                quiet=True,
                playbook=f"/tmp/{playbook_name}.yaml",
                private_data_dir="/tmp",
                extravars=extra_vars,
                event_handler=self.my_event_handler,
                status_handler=self.my_status_handler,
            )
        except Exception as e:
            print(f"Error running playbook: {e}")

        thread.join()

        return runner.status, self.data


async def pull_from_mq():
    try:
        while True:
            # add some polling delay to avoid running too often
            await asyncio.sleep(5 * random.uniform(0.7, 1.3))

            with db.pool.connection() as conn:
                with conn.cursor() as cur:
                    with conn.transaction():
                        rs = cur.execute(
                            """
                            SELECT * 
                            FROM mq 
                            WHERE now() > start_after 
                            LIMIT 1 
                            FOR UPDATE SKIP LOCKED
                            """
                        ).fetchone()

                        if rs is None:
                            continue

                        msg = Msg(*rs)

                        match msg.msg_type:
                            case "CREATE_CLUSTER":
                                print("Processing a CREATE_CLUSTER")
                                create_cluster(msg.msg_id, msg.msg_data, msg.created_by)

                            case "RECREATE_CLUSTER":
                                print("Processing a RECREATE_CLUSTER")
                                create_cluster(
                                    msg.msg_id, msg.msg_data, msg.created_by, True
                                )
                            case "DELETE_CLUSTER":
                                print("Processing a DELETE_CLUSTER")
                                delete_cluster(msg.msg_id, msg.msg_data)

                            case "SCALE_CLUSTER":
                                print("Processing a SCALE_CLUSTER")
                                scale_cluster(msg.msg_id, msg.msg_data, msg.created_by)

                            case "FAIL_ZOMBIE_JOBS":
                                print("Processing a FAIL_ZOMBIE_JOBS")
                                fail_zombie_jobs()

                            case "HEALTHCHECK_CLUSTERS":
                                print("Processing a HEALTHCHECK_CLUSTERS")
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
