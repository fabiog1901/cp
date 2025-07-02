import datetime as dt
from dataclasses import dataclass
from typing import Any
from uuid import UUID

TS_FORMAT = "YYYY-MM-DD HH:mm:ss"

"""
Created
Pending
Running
Paused (or Suspended)
Retrying
Succeeded (or Completed)
Failed
Canceled (or Aborted)
Archived

NotInstalled
Installing
Installed
Configuring
Starting
Running
Paused
Stopping
Stopped
Upgrading
Degraded
Unresponsive
Failed
Terminated
Archived
Unknown

"""


@dataclass
class WebUser:
    username: str
    roles: list[str]
    groups: list[str]


@dataclass
class User:
    username: str
    password_hash: str
    salt: bytes
    hash_algo: str
    iterations: int
    attempts: int
    groups: list[str]


@dataclass
class GroupRoleMap:
    role: str
    groups: list[str]


@dataclass
class StrID:
    id: str


@dataclass
class IntID:
    id: int

@dataclass
class Region:
    cloud: str
    region: str
    zone: str
    vpc_id: str
    security_groups: list[str]
    subnet: str
    image: str
    extras: dict
    tags: dict


@dataclass
class Msg:
    msg_id: str
    start_after: dt.datetime
    msg_type: str
    msg_data: dict
    created_at: dt.datetime
    created_by: str


@dataclass
class ClusterOverview:
    cluster_id: str
    grp: str
    created_by: str
    status: str
    version: str
    node_count: int
    node_cpus: int
    disk_size: int

@dataclass
class InventoryRegion:
    cloud: str
    region: str
    nodes: list[str]

@dataclass
class InventoryLB:
    cloud: str
    region: str
    dns_address: str

@dataclass
class Cluster:
    cluster_id: str
    cluster_inventory: list[InventoryRegion]
    lbs_inventory: list[InventoryLB]
    version: str
    node_count: int
    node_cpus: int
    disk_size: int
    status: str
    grp: str
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime
    updated_by: str


@dataclass
class ClusterRequest:
    name: str
    node_count: int
    node_cpus: int
    disk_size: int
    regions: list[str]
    version: str
    group: str

@dataclass
class ClusterUpgradeRequest:
    name: str
    version: str
    auto_finalize: bool

@dataclass
class ClusterScaleRequest:
    name: str
    node_count: int
    node_cpus: int
    disk_size: int
    regions: list[str]


@dataclass
class Job:
    job_id: int
    job_type: str
    status: str
    description: dict[str, int | str | list[str]]
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime


@dataclass
class Task:
    job_id: UUID
    task_id: UUID
    created_at: dt.datetime
    task_name: str | None
    task_desc: str | None


@dataclass
class EventLog:
    created_at: dt.datetime
    created_by: str
    event_type: str
    details: str
