import json
import os
import shutil
import time

import ansible_runner
import requests

from .. import db
from ..models import JobState

PLAYBOOKS_URL_CACHE_VALID_UNTIL = 0

PLAYBOOKS_URL = ""


def refresh_cache():
    global PLAYBOOKS_URL
    global PLAYBOOKS_URL_CACHE_VALID_UNTIL

    PLAYBOOKS_URL = db.get_setting("playbooks_url")

    PLAYBOOKS_URL_CACHE_VALID_UNTIL = time.time() + int(
        db.get_setting("playbooks_url_cache_expiry")
    )


class MyRunner:
    def __init__(
        self,
        job_id: int,
        counter: int = 0,
    ):
        self.data = {}
        self.job_id = job_id
        self.counter = counter

        if time.time() > PLAYBOOKS_URL_CACHE_VALID_UNTIL:
            refresh_cache()

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
            "runner_retry",
            "playbook_on_include",
        ]:
            return

        elif e["event"] == "runner_on_ok":
            if e.get("event_data")["task"] == "Data":
                self.data = e["event_data"]["res"]["msg"]
            else:
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
            self.counter,
            e["created"],
            task_type,
            task_data,
        )

        self.counter += 1

    def launch_runner(
        self, playbook_name: str, extra_vars: dict
    ) -> tuple[str, dict, int]:

        r = requests.get(PLAYBOOKS_URL + playbook_name + ".yaml")

        # create a new working directory
        shutil.rmtree(f"/tmp/job-{self.job_id}", ignore_errors=True)
        os.mkdir(path=f"/tmp/job-{self.job_id}")

        with open(f"/tmp/job-{self.job_id}/playbook.yaml", "wb") as f:
            f.write(r.content)

        db.update_job(self.job_id, JobState.RUNNING)

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
            db.update_job(self.job_id, JobState.FAILED)
            print(f"Error running playbook: {e}")

        heartbeat_ts = time.time() + 60
        while thread.is_alive():
            # send hb messsage periodically
            if time.time() > heartbeat_ts:
                db.update_job(self.job_id, JobState.RUNNING)
                heartbeat_ts = time.time() + 60

            time.sleep(1)

        # update the Job status
        if runner.status == "successful":
            db.update_job(self.job_id, JobState.COMPLETED)
        else:
            db.update_job(self.job_id, JobState.FAILED)

        # rm -rf job-directory
        shutil.rmtree(f"/tmp/job-{self.job_id}", ignore_errors=True)

        return runner.status, self.data, self.counter


class MyRunnerLite:
    def __init__(
        self,
        job_id: int,
    ):
        self.data = {}
        self.job_id = job_id

        if time.time() > PLAYBOOKS_URL_CACHE_VALID_UNTIL:
            refresh_cache()

    def my_status_handler(self, status, runner_config):
        return

    def my_event_handler(self, e):
        if e["event"] == "runner_on_ok":
            if e.get("event_data")["task"] == "Data":
                self.data = e["event_data"]["res"]["msg"]

    def launch_runner(self, playbook_name: str, extra_vars: dict) -> tuple[str, dict]:
        r = requests.get(PLAYBOOKS_URL + playbook_name + ".yaml")

        # create a new working directory
        shutil.rmtree(f"/tmp/job-{self.job_id}", ignore_errors=True)
        os.mkdir(path=f"/tmp/job-{self.job_id}")

        with open(f"/tmp/job-{self.job_id}/playbook.yaml", "wb") as f:
            f.write(r.content)

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
            print(f"Error running playbook: {e}")

        thread.join()

        # rm -rf job-directory
        shutil.rmtree(f"/tmp/job-{self.job_id}", ignore_errors=True)

        return runner.status, self.data
