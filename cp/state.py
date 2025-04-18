import reflex as rx
import asyncio
from uuid import UUID
from .cp import app

from .models import *
from . import db
from . import runner


class State(rx.State):
    current_job: Job = None
    current_cluster: Cluster = None
    jobs: list[Job] = []
    jobs_len: int = 0

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    @rx.var
    def job_id(self) -> str | None:
        return self.router.page.params.get("j_id") or None

    @rx.event
    def get_cluster(self, cluster_id):
        self.current_cluster = db.get_cluster(cluster_id)

    @rx.event
    def get_job(self, cluster_id, job_id):
        self.current_job = db.get_job(cluster_id, job_id)

    @rx.event
    def load_jobs(self):
        # self.jobs = db.get_all_jobs(self.current_cluster.cluster_id)
        self.jobs_len = len(self.jobs)

    @rx.event
    def load_tasks(self):
        # self.tasks = db.get_all_tasks(self.current_cluster.cluster_id, self.current_job.job_id)
        self.tasks_len = len(self.tasks)
