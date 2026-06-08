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
from .maintenance import (
    FAIL_ZOMBIE_JOBS_MESSAGE_TYPE,
    create_fail_zombie_jobs_handler,
)
from .router import create_jobs_router
from .service import JobsService
from .types import (
    ClusterIDRef,
    IntID,
    Job,
    JobDetailsResponse,
    JobID,
    JobRescheduleResponse,
    JobStatsResponse,
    QueueMessage,
    Task,
)
from .worker import create_queue_worker, run_queue_worker

__all__ = [
    "ClusterIDRef",
    "FAIL_ZOMBIE_JOBS_MESSAGE_TYPE",
    "IntID",
    "JOB_CLUSTER_MAP_TABLE",
    "JOBS_TABLE",
    "Job",
    "JobDetailsResponse",
    "JobID",
    "JobRescheduleResponse",
    "JobStatsResponse",
    "JobsRepositoryMixin",
    "JobsService",
    "QUEUE_TABLE",
    "QueueMessage",
    "QueueJobRepositoryMixin",
    "QueueRepositoryMixin",
    "TASKS_TABLE",
    "Task",
    "create_fail_zombie_jobs_handler",
    "create_queue_worker",
    "create_jobs_router",
    "run_queue_worker",
]
