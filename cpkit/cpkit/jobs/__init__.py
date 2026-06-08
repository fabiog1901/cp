"""Framework-owned job queue primitives."""

from .repository import (
    JOB_CLUSTER_MAP_TABLE,
    JOBS_TABLE,
    QUEUE_TABLE,
    TASKS_TABLE,
    JobsRepositoryMixin,
    QueueJobRepositoryMixin,
    QueueRepositoryMixin,
)
from .service import JobsService
from .types import (
    ClusterIDRef,
    IntID,
    Job,
    JobID,
    JobStatsResponse,
    QueueMessage,
    Task,
)
from .worker import run_queue_worker

__all__ = [
    "ClusterIDRef",
    "IntID",
    "JOB_CLUSTER_MAP_TABLE",
    "JOBS_TABLE",
    "Job",
    "JobID",
    "JobStatsResponse",
    "JobsRepositoryMixin",
    "JobsService",
    "QUEUE_TABLE",
    "QueueMessage",
    "QueueJobRepositoryMixin",
    "QueueRepositoryMixin",
    "TASKS_TABLE",
    "Task",
    "run_queue_worker",
]
