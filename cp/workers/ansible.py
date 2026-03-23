import datetime as dt
import gzip
import json
import logging
import os
import shutil
import time

import ansible_runner
import yaml

from ..infra import get_repo
from ..models import JobState, Playbook

logger = logging.getLogger(__name__)


class MyRunner:
    def __init__(
        self,
        job_id: int,
        counter: int = 0,
    ):
        self.data = {}
        self.job_id = job_id
        self.counter = counter
        self.repo = get_repo()

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

        self.repo.insert_task(
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
        job_dir = f"/tmp/job-{self.job_id}"
        try:
            p: Playbook = self.repo.get_default_playbook(playbook_name)
            if p is None or p.playbook is None:
                raise RuntimeError(
                    f"Default playbook '{playbook_name}' is not configured"
                )

            shutil.rmtree(job_dir, ignore_errors=True)
            os.makedirs(job_dir, exist_ok=True)
            self.repo.update_job(self.job_id, JobState.RUNNING)

            thread, runner = ansible_runner.run_async(
                quiet=False,
                verbosity=1,
                playbook=yaml.safe_load(gzip.decompress(p.playbook).decode()),
                private_data_dir=job_dir,
                extravars=extra_vars,
                event_handler=self.my_event_handler,
                status_handler=self.my_status_handler,
            )
        except Exception as err:
            self.repo.update_job(self.job_id, JobState.FAILED)
            self.repo.insert_task(
                self.job_id,
                self.counter,
                dt.datetime.now(dt.timezone.utc),
                "FAILURE",
                str(err),
            )
            logger.exception(
                "Error starting playbook '%s' for job %s",
                playbook_name,
                self.job_id,
            )
            shutil.rmtree(job_dir, ignore_errors=True)
            return "failed", self.data, self.counter + 1

        heartbeat_ts = time.time() + 60
        try:
            while thread.is_alive():
                if time.time() > heartbeat_ts:
                    self.repo.update_job(self.job_id, JobState.RUNNING)
                    heartbeat_ts = time.time() + 60

                time.sleep(1)

            if runner.status == "successful":
                self.repo.update_job(self.job_id, JobState.COMPLETED)
            else:
                self.repo.update_job(self.job_id, JobState.FAILED)
        except Exception:
            self.repo.update_job(self.job_id, JobState.FAILED)
            logger.exception(
                "Error while monitoring playbook '%s' for job %s",
                playbook_name,
                self.job_id,
            )
            return "failed", self.data, self.counter
        finally:
            shutil.rmtree(job_dir, ignore_errors=True)

        return runner.status, self.data, self.counter


class MyRunnerLite:
    def __init__(
        self,
        job_id: int,
    ):
        self.data = {}
        self.job_id = job_id
        self.repo = get_repo()

    def my_status_handler(self, status, runner_config):
        return

    def my_event_handler(self, e):
        if e["event"] == "runner_on_ok":
            if e.get("event_data")["task"] == "Data":
                self.data = e["event_data"]["res"]["msg"]

    def launch_runner(self, playbook_name: str, extra_vars: dict) -> tuple[str, dict]:
        job_dir = f"/tmp/job-{self.job_id}"
        try:
            p: Playbook = self.repo.get_default_playbook(playbook_name)
            if p is None or p.playbook is None:
                raise RuntimeError(
                    f"Default playbook '{playbook_name}' is not configured"
                )

            shutil.rmtree(job_dir, ignore_errors=True)
            os.makedirs(job_dir, exist_ok=True)

            thread, runner = ansible_runner.run_async(
                quiet=False,
                verbosity=1,
                playbook=gzip.decompress(p.playbook).decode(),
                private_data_dir=job_dir,
                extravars=extra_vars,
                event_handler=self.my_event_handler,
                status_handler=self.my_status_handler,
            )
        except Exception:
            logger.exception(
                "Error starting playbook '%s' for job %s",
                playbook_name,
                self.job_id,
            )
            shutil.rmtree(job_dir, ignore_errors=True)
            return "failed", self.data

        try:
            thread.join()
        finally:
            shutil.rmtree(job_dir, ignore_errors=True)

        return runner.status, self.data
