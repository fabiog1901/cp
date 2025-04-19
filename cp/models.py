from dataclasses import dataclass
import datetime as dt
from uuid import UUID
from typing import Any


@dataclass
class MsgID:
    msg_id: str


@dataclass
class Playbook:
    playbook_id: str
    playbook: dict


@dataclass
class Msg:
    msg_id: str
    msg_type: str
    msg_data: dict
    created_at: dt.datetime
    created_by: str


@dataclass
class ClusterOverview:
    cluster_id: str
    created_by: str
    status: str


@dataclass
class Cluster:
    cluster_id: str
    topology: Any | None
    status: str
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime
    updated_by: str


@dataclass
class ClusterRequest:
    name: str
    node_count: int
    node_cpus: int
    regions: list[str]
    version: str


@dataclass
class Job:
    job_id: int
    job_type: str
    status: str
    created_at: dt.datetime
    created_by: str


@dataclass
class Task:
    job_id: UUID
    task_id: UUID
    progress: int
    created_at: dt.datetime
    task_name: str | None
    task_desc: str | None


@dataclass
class EventLog:
    created_at: dt.datetime
    created_by: str
    event_type: str
    details: str
