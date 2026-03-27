import datetime as dt
from enum import StrEnum, auto
from typing import Any, Callable, Dict, List, Optional, Union

from pydantic import BaseModel, Field

TS_FORMAT = "YYYY-MM-DD HH:mm:ss"
STRFTIME = "%Y-%m-%d %H:%M:%S"


class AutoNameStrEnum(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name


#
# ENUMS FOR TYPES AND STATES
#
class PlaybookName(AutoNameStrEnum):
    CREATE_CLUSTER = auto()
    DELETE_CLUSTER = auto()
    SCALE_CLUSTER_IN = auto()
    SCALE_CLUSTER_OUT = auto()
    SCALE_DISK_SIZE = auto()
    SCALE_NODE_CPUS = auto()
    UPGRADE_CLUSTER = auto()
    HEALTHCHECK_CLUSTER = auto()
    RESTORE_CLUSTER = auto()


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


class Event(AutoNameStrEnum):
    LOGIN = auto()
    LOGOUT = auto()
    UPDATE_PLAYBOOK = auto()
    API_KEY_CREATE = auto()
    API_KEY_DELETE = auto()
    SETTING_UPDATE = auto()
    SETTING_RESET = auto()
    VERSION_ADD = auto()
    VERSION_REMOVE = auto()
    DB_USER_UPDATE = auto()
    DB_USER_ADD_ROLE = auto()
    DB_USER_REMOVE_ROLE = auto()
    DB_USER_ADD = auto()
    DB_USER_REMOVE = auto()
    REGION_ADD = auto()
    REGION_REMOVE = auto()
    PLAYBOOK_ADD = auto()
    PLAYBOOK_REMOVE = auto()
    PLAYBOOK_SET_DEFAULT = auto()


class CPRole(AutoNameStrEnum):
    CP_READONLY = auto()
    CP_USER = auto()
    CP_ADMIN = auto()


class SettingKey(AutoNameStrEnum):
    cloud_storage_url = auto()
    default_password = auto()
    default_username = auto()
    licence_key = auto()
    licence_org = auto()
    playbooks_url = auto()
    playbooks_url_cache_expiry = auto()
    prom_url = auto()
    sso_auth_url = auto()
    sso_cache_expiry = auto()
    sso_claim_name = auto()
    sso_client_id = auto()
    sso_client_secret = auto()
    sso_issuer = auto()
    sso_jwks_url = auto()
    sso_redirect_uri = auto()
    sso_token_url = auto()
    sso_userinfo_url = auto()
    #
    CP_ENTERPRISE_LICENSE_KEY = auto()
    OIDC_ENABLED = auto()
    OIDC_ISSUER_URL = auto()
    OIDC_CLIENT_ID = auto()
    OIDC_CLIENT_SECRET = auto()
    OIDC_SCOPES = auto()
    OIDC_AUDIENCE = auto()
    OIDC_EXTRA_AUTH_PARAMS = auto()
    OIDC_REDIRECT_URI = auto()
    OIDC_LOGIN_PATH = auto()
    OIDC_SESSION_COOKIE_NAME = auto()
    OIDC_STATE_COOKIE_NAME = auto()
    OIDC_NONCE_COOKIE_NAME = auto()
    OIDC_NEXT_COOKIE_NAME = auto()
    OIDC_COOKIE_SECURE = auto()
    OIDC_COOKIE_SAMESITE = auto()
    OIDC_COOKIE_DOMAIN = auto()
    OIDC_VERIFY_AUDIENCE = auto()
    OIDC_UI_USERNAME_CLAIM = auto()
    OIDC_AUTHZ_READONLY_GROUPS = auto()
    OIDC_AUTHZ_USER_GROUPS = auto()
    OIDC_AUTHZ_ADMIN_GROUPS = auto()
    OIDC_AUTHZ_GROUPS_CLAIM = auto()


#
# GENERIC / LEGACY
#
class JobID(BaseModel):
    job_id: int


class ClusterIDRef(BaseModel):
    cluster_id: str


class StrID(BaseModel):
    id: str


class IntID(BaseModel):
    id: int


#
# AUTH AND LOGGING
#
class WebUser(BaseModel):
    username: str
    roles: List[str]
    groups: List[str]


class RoleGroupMap(BaseModel):
    role: str
    groups: List[str]


class EventCountResponse(BaseModel):
    total: int


#
# CLUSTER
#
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
    backup_type: str
    start_time: dt.datetime | None
    end_time: dt.datetime


class BackupPathOption(BaseModel):
    path: str


class DatabaseUser(BaseModel):
    username: str
    options: list[str] | None
    member_of: list[str] | None


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


class JobDetailsResponse(BaseModel):
    job: Job
    description_yaml: str
    tasks: List[Task]
    linked_clusters: List[ClusterIDRef]


class JobRescheduleResponse(BaseModel):
    job_id: int


#
# ADMIN
#
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


class RegionOption(BaseModel):
    region_id: str


class NodeCountOption(BaseModel):
    node_count: int


class CpuCountOption(BaseModel):
    cpu_count: int


class DiskSizeOption(BaseModel):
    size_gb: int


class Nodes(BaseModel):
    cluster_id: str
    nodes: list[str]


#
# PLAYBOOK
#
class PlaybookOverview(BaseModel):
    name: PlaybookName
    version: dt.datetime
    default_version: dt.datetime | None = None
    created_at: dt.datetime
    created_by: str
    updated_by: str | None = None


class Playbook(PlaybookOverview):
    content: bytes | None = None


class PlaybookResponse(BaseModel):
    name: str
    version: str
    default_version: str
    available_versions: list[str]
    original_content: str
    modified_content: str


class PlaybookVersionResponse(BaseModel):
    playbook_version: str
    original_content: str
    modified_content: str
    available_versions: list[str] | None = None
    default_version: str | None = None


class PlaybookSaveRequest(BaseModel):
    content: str


class DashboardMetrics(BaseModel):
    current_nodes: list[int]
    chart_data: list[dict[str, Any]]


class DashboardSnapshot(BaseModel):
    cluster: Cluster
    metrics: DashboardMetrics


class ClusterJobsSnapshot(BaseModel):
    cluster: Cluster
    jobs: list[Job]


class ClusterUsersSnapshot(BaseModel):
    cluster: Cluster
    database_users: list[DatabaseUser]


class ClusterBackupsSnapshot(BaseModel):
    cluster: Cluster
    backup_paths: list[BackupPathOption]


class ClusterCreateOptionsResponse(BaseModel):
    versions: list[str]
    node_counts: list[int]
    cpus_per_node: list[int]
    disk_sizes: list[int]
    regions: list[RegionOption]


class ClusterDialogOptionsResponse(BaseModel):
    node_counts: list[int]
    cpus_per_node: list[int]
    disk_sizes: list[int]
    regions: list[RegionOption]
    upgrade_versions: list[str]


class ClusterCreateApiRequest(BaseModel):
    name: str
    node_count: int
    node_cpus: int
    disk_size: int
    regions: list[str]
    version: str
    group: str


class ClusterUpgradeRequest(BaseModel):
    name: str
    version: str
    auto_finalize: bool


class ClusterRestoreApiRequest(BaseModel):
    backup_path: str
    restore_aost: str | None = None
    restore_full_cluster: bool
    object_type: str | None = None
    object_name: str | None = None
    backup_into: str | None = None


class ClusterRoleRevokeRequest(BaseModel):
    role: str


class ClusterPasswordUpdateRequest(BaseModel):
    password: str


class NoFreeComputeUnitError(Exception):
    pass


class ComputeUnitNotFoundError(Exception):
    pass


class ComputeUnitStateError(Exception):
    pass


class ComputeUnitOperationError(Exception):
    pass


class AllocatePlaybookError(Exception):
    pass


class ApiKeyNotFoundError(Exception):
    pass


class InvalidApiKeyValidityError(Exception):
    pass


class SettingNotFoundError(Exception):
    pass


class SettingRecord(BaseModel):
    key: SettingKey
    value: str | None = None
    default_value: str
    value_type: str
    category: str
    is_secret: bool = False
    description: str = ""
    updated_at: dt.datetime
    updated_by: str | None = None


class SettingUpdateRequest(BaseModel):
    value: str


class LogMsg(BaseModel):
    ts: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    user_id: str
    action: str
    details: dict[str, Any] | None = None
    request_id: str | None = None


class ApiKeyRecord(BaseModel):
    access_key: str
    encrypted_secret_access_key: bytes
    owner: str
    valid_until: dt.datetime
    roles: list[CPRole] | None = None


class ApiKeySummary(BaseModel):
    access_key: str
    owner: str
    valid_until: dt.datetime
    roles: list[CPRole] | None = None


class ApiKeyCreateRequest(BaseModel):
    valid_until: dt.datetime
    roles: list[CPRole] | None = None


class ApiKeyCreateRequestInDB(ApiKeyCreateRequest):
    access_key: str


class ApiKeyCreateResponse(ApiKeySummary):
    secret_access_key: str


class DeferredTask(BaseModel):
    fn: Callable[..., None]
    args: tuple | None
    kwargs: dict = {}
