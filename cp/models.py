import datetime as dt
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

TS_FORMAT = "YYYY-MM-DD HH:mm:ss"
STRFTIME = "%Y-%m-%d %H:%M:%S"

from enum import StrEnum, auto


class AutoNameStrEnum(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name


# ENUMS FOR TYPES AND STATES


class EventType(AutoNameStrEnum):
    LOGIN = auto()
    LOGOUT = auto()
    UPDATE_SETTING = auto()
    VERSION_ADD = auto()
    VERSION_REMOVE = auto()
    DB_USER_UPDATE = auto()
    DB_USER_ADD_ROLE = auto()
    DB_USER_REMOVE_ROLE = auto()
    DB_USER_ADD = auto()
    DB_USER_REMOVE = auto()
    PLAYBOOK_ADD = auto()
    REGION_ADD = auto()
    REGION_REMOVE = auto()
    PLAYBOOK_ADD = auto()
    PLAYBOOK_REMOVE = auto()
    PLAYBOOK_SET_DEFAULT = auto()


class JobType(AutoNameStrEnum):
    CREATE_CLUSTER = auto()
    RECREATE_CLUSTER = auto()
    DELETE_CLUSTER = auto()
    SCALE_CLUSTER = auto()
    UPGRADE_CLUSTER = auto()
    DEBUG_CLUSTER = auto()
    RESTORE_CLUSTER = auto()
    HEALTHCHECK_CLUSTERS = auto()
    FAIL_ZOMBIE_JOBS = auto()


class ClusterState(AutoNameStrEnum):
    PROVISIONING = auto()
    RUNNING = auto()
    UNHEALTHY = auto()
    FAILED = auto()
    SCALING = auto()
    SCALE_FAILED = auto()
    RESTORING = auto()
    RESTORE_FAILED = auto()
    DELETING = auto()
    DELETED = auto()
    DELETE_FAILED = auto()
    UPGRADING = auto()
    UPGRADE_FAILED = auto()


class JobState(AutoNameStrEnum):
    RUNNING = auto()
    FAILED = auto()
    SCHEDULED = auto()
    COMPLETED = auto()


# AUTH AND LOGGING


class WebUser(BaseModel):
    username: str
    roles: List[str]
    groups: List[str]


class RoleGroupMap(BaseModel):
    role: str
    groups: List[str]


class EventLog(BaseModel):
    created_at: dt.datetime
    created_by: str
    event_type: str
    event_details: Dict[str, Union[int, str, List[str]]]


class EventLogYaml(BaseModel):
    created_at: dt.datetime
    created_by: str
    event_type: str
    event_details_yaml: str


# CLUSTER


class ClusterOverview(BaseModel):
    cluster_id: str
    grp: str
    created_by: str
    status: str
    version: str
    node_count: int
    node_cpus: int
    disk_size: int


class InventoryRegion(BaseModel):
    cloud: str
    region: str
    nodes: List[str]


class InventoryLB(BaseModel):
    cloud: str
    region: str
    dns_address: str


class Cluster(BaseModel):
    cluster_id: str
    cluster_inventory: List[InventoryRegion]
    lbs_inventory: List[InventoryLB]
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


class ClusterRequest(BaseModel):
    name: str
    node_count: int
    node_cpus: int
    disk_size: int
    regions: List[str]
    version: str
    group: str


class ClusterUpgradeRequest(BaseModel):
    name: str
    version: str
    auto_finalize: bool


class RestoreRequest(BaseModel):
    name: str
    backup_path: str
    restore_aost: str | None
    restore_full_cluster: bool
    object_type: str | None
    object_name: str | None
    backup_into: str | None


class ClusterScaleRequest(BaseModel):
    name: str
    node_count: int
    node_cpus: int
    disk_size: int
    regions: List[str]


class BackupDetails(BaseModel):
    database_name: str | None
    parent_schema_name: str | None
    object_name: str
    object_type: str
    end_time: dt.datetime


class DatabaseUser(BaseModel):
    username: str
    options: str | None
    member_of: list[str | None]


class NewDatabaseUserRequest(BaseModel):
    username: str
    password: str


# JOBS


class Msg(BaseModel):
    msg_id: int
    start_after: dt.datetime
    msg_type: str
    msg_data: Dict[str, Any]
    created_at: dt.datetime
    created_by: str


class Job(BaseModel):
    job_id: int
    job_type: str
    status: str
    description: Dict[str, Union[int, str, List[str], None]]
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime


class Task(BaseModel):
    job_id: int
    task_id: int
    created_at: dt.datetime
    task_name: Optional[str]
    task_desc: Optional[str]


# ADMIN


class Region(BaseModel):
    cloud: str
    region: str
    zone: str
    vpc_id: str
    security_groups: List[str]
    subnet: str
    image: str
    extras: Dict[str, Any]


class Version(BaseModel):
    version: str


class Setting(BaseModel):
    id: str
    value: str
    updated_at: dt.datetime
    updated_by: str
    default_value: str
    description: str


class Nodes(BaseModel):
    cluster_id: str
    nodes: list[str]


class PlaybookOverview(BaseModel):
    name: str
    version: dt.datetime
    default_version: dt.datetime | None = None
    created_at: dt.datetime
    created_by: str
    updated_by: str | None = None


class Playbook(PlaybookOverview):
    playbook: bytes | None = None


# GENERIC


class StrID(BaseModel):
    id: str


class IntID(BaseModel):
    id: int
