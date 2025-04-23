import threading
import time
import datetime as dt
from pathlib import Path
import os
import yaml
import datetime as dt
import ansible_runner
import json
from pprint import pprint

from .models import Play, PlayTask, ClusterRequest, Region, Cluster
from . import db
from dataclasses import asdict

completed_tasks = 0
progress = 0


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
) -> None:

    cluster_request = ClusterRequest(**cluster)

    c = db.get_cluster(cluster_request.name)
    if c and c.status == "OK":
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
        cluster_request.name,
        "PROVISIONING",
        "root",
        "root",
    )

    db.create_job_linked(
        cluster_request.name,
        job_id,
        "CREATE_CLUSTER",
        "STARTED",
        "root",
    )

    threading.Thread(
        target=create_cluster_worker,
        args=(
            job_id,
            cluster_request,
        ),
    ).start()


def create_cluster_worker(job_id, cluster_request: ClusterRequest):
    playbook = []

    plays = db.get_plays("CREATE_CLUSTER")

    for play in plays:

        tasks = db.get_play_tasks("CREATE_CLUSTER", play.play_order)

        play.play["tasks"] = [x.task for x in tasks]

        playbook.append(play.play)

    deployment = []

    for cloud_region in cluster_request.regions:

        cloud, region = cloud_region.split(":")

        env_details: list[Region] = db.get_region(cloud, region)

        # add 1 HAProxy per region
        deployment.append(
            {
                "cluster_name": cluster_request.name,
                "copies": 1,
                "inventory_groups": ["haproxy"],
                "exact_count": 1,
                "instance": {"cpu": 4},
                "instance_type": "e2-medium",
                "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                "tags": {"Name": f"{cluster_request.name}-lb"},
                "groups": [
                    {
                        "user": "ubuntu",
                        "public_ip": True,
                        "public_key_id": "workshop",
                        "tags": {"owner": "fabio"},
                        "cloud": cloud,
                        "image": env_details[0].image,
                        "region": region,
                        "vpc_id": env_details[0].vpc_id,
                        "security_groups": env_details[0].security_groups,
                        "zone": env_details[0].zone,
                        "subnet": env_details[0].subnet,
                    }
                ],
            }
            | env_details[0].extras
        )

        # distribute the node_counts over all available zones

        node_count_per_zone = get_node_count_per_zone(
            len(env_details), cluster_request.node_count
        )

        for idx, zone_count in enumerate(node_count_per_zone):
            deployment.append(
                {
                    "cluster_name": cluster_request.name,
                    "copies": 1,
                    "inventory_groups": ["cockroachdb"],
                    "exact_count": zone_count,
                    "instance": {"cpu": cluster_request.node_cpus},
                    "instance_type": "e2-medium",
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
                            "image": env_details[idx].image,
                            "region": region,
                            "vpc_id": env_details[idx].vpc_id,
                            "security_groups": env_details[idx].security_groups,
                            "zone": env_details[idx].zone,
                            "subnet": env_details[idx].subnet,
                        }
                    ],
                }
                | env_details[0].extras
            )

    extra_vars = {
        "state": "present",
        "owner": "fabio",
        "deployment_id": cluster_request.name,
        "deployment": deployment,
        "certificates_organization_name": "{{ owner }}-org",
        "certificates_dir": "certs",
        "certificates_usernames": ["root"],
        "certificates_hosts": "{{ groups['cockroachdb'] }}",
        "certificates_loadbalancer": "{{ groups['haproxy'] | default('') }}",
        "cockroachdb_deployment": "standard",
        "cockroachdb_secure": True,
        "cockroachdb_certificates_dir": "certs",
        "cockroachdb_certificates_clients": ["root"],
        "cockroachdb_version": cluster_request.version,
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

    total_tasks = sum(len(play.get("tasks", [])) for play in playbook)

    def my_status_handler(status, runner_config):
        return

    def my_event_handler(e):
        global completed_tasks, progress

        task_type = ""
        task_data = ""

        if e["event"] in [
            "verbose",
            "playbook_on_no_hosts_matched",
            "runner_on_skipped",
            "runner_item_on_skipped",
            "runner_item_on_ok",
            "runner_on_ok",
            "playbook_on_include",
        ]:
            return

        elif e["event"] == "warning":
            task_type = "WARNING"
            task_data = e["stdout"]

        elif e["event"] == "error":
            task_type = "ERROR"
            task_data = e["stdout"]

        elif e["event"] == "playbook_on_start":
            return

        elif e["event"] == "playbook_on_play_start":
            task_type = f"PLAY [{e['event_data']['play']}]"

        elif e["event"] == "playbook_on_task_start":
            completed_tasks += 1
            progress = int((completed_tasks / total_tasks) * 100)
            task_type = f"TASK [{e['event_data']['task']}]"

        elif e["event"] == "runner_on_start":
            return

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
            task_type = e["event"]
            task_data = json.dumps(e)
            print(f"==========> this is a new event! {e}")

        db.create_task(
            job_id,
            e["counter"],
            progress,
            e["created"],
            task_type,
            task_data,
        )

    # Execute the playbook
    try:
        thread, runner = ansible_runner.run_async(
            quiet=False,
            playbook=playbook,
            private_data_dir="/tmp",
            extravars=extra_vars,
            event_handler=my_event_handler,
            status_handler=my_status_handler,
        )
    except Exception as e:
        raise Exception(f"Error running playbook: {e}")

    # wait for the Runner thread to complete
    db.update_job(job_id, "RUNNING")
    thread.join()

    # resetting for next execution
    global completed_tasks, progress
    completed_tasks = 0
    progress = 0

    if runner.status == "successful":
        db.update_job(job_id, "COMPLETED")
        db.update_cluster(
            cluster_request.name,
            "OK",
            {"lbs": ["10.10.15.48", "10.10.68.175"]},
            "root",
        )

    else:
        db.update_job(job_id, "FAILED")
        db.update_cluster(
            cluster_request.name,
            "FAILED",
            {},
            "root",
        )
