import threading
import time
import datetime as dt
from pathlib import Path
import os
import yaml
import datetime as dt
import ansible_runner
import json

from .models import Playbook, ClusterRequest
from . import db

completed_tasks = 0
progress = 0


def create_cluster(
    job_id: int,
    cluster: dict,
) -> None:
    cluster_request = ClusterRequest(**cluster)

    c = db.get_cluster(cluster_request.name)
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
    playbook = db.get_playbook("CREATE_CLUSTER").playbook

    extra_vars = {
        "state": "present",
        "deployment_id": cluster_request.name,
        "deployment": [
            {
                "cluster_name": "fab1",
                "copies": 1,
                "inventory_groups": ["haproxy"],
                "exact_count": 0,
                "instance": {"cpu": 4},
                "volumes": {"os": {"size": 20, "type": "standard_ssd"}, "data": []},
                "tags": {"Name": "fabio-app"},
                "groups": [
                    {
                        "user": "ubuntu",
                        "public_ip": True,
                        "public_key_id": "workshop",
                        "tags": {"owner": "fabio"},
                        "cloud": "aws",
                        "image": "/canonical/ubuntu/server/24.04",
                        "region": "us-east-1",
                        "vpc_id": "vpc-039dd158f86366108",
                        "security_groups": ["sg-067d280fe7a21bc60"],
                        "zone": "a",
                        "subnet": "subnet-0d933a012de53be58",
                    }
                ],
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

        if e["event"] == "verbose":
            return

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

        elif e["event"] == "runner_on_ok":
            task_data = f"ok: [{e['event_data']['host']}]"

        elif e["event"] == "runner_on_failed":
            task_data = f"fatal: [{e['event_data']['host']}]\n{json.dumps(e['event_data']['res']['msg'])}"

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
            playbook=playbook,
            private_data_dir="/tmp",
            extravars=extra_vars,
            event_handler=my_event_handler,
            status_handler=my_status_handler,
        )
    except Exception as e:
        raise Exception(f"Error running playbook: {e}")

    # wait for the Runner thread to complete
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
            {"lbs": ["10.10.15.48", "10.10.68.175"]},
            "root",
        )
