import datetime as dt
from enum import StrEnum, auto
from typing import Any, Callable, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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


class CommandType(AutoNameStrEnum):
    CREATE_CLUSTER = auto()
    RECREATE_CLUSTER = auto()
    DELETE_CLUSTER = auto()
    SCALE_CLUSTER = auto()
    UPGRADE_CLUSTER = auto()
    DEBUG_CLUSTER = auto()
    RESTORE_CLUSTER = auto()
    RESTORE_CLUSTER_OBJECT = auto()
    RESTORE_FULL_CLUSTER = auto()
    POLL_CLUSTER_RESTORE = auto()
    SYNC_BACKUP_CATALOG = auto()
    SYNC_CLUSTER_BACKUP_CATALOG = auto()
    HEALTHCHECK_CLUSTERS = auto()
    FAIL_ZOMBIE_JOBS = auto()


class ClusterState(AutoNameStrEnum):
    CREATING = auto()
    ACTIVE = auto()
    UNHEALTHY = auto()
    CREATE_FAILED = auto()
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
    QUEUED = auto()
    COMPLETED = auto()


class AuditEvent(AutoNameStrEnum):
    LOGIN = auto()
    LOGOUT = auto()
    API_KEY_CREATED = auto()
    API_KEY_DELETED = auto()
    SETTING_UPDATED = auto()
    SETTING_RESET = auto()
    VERSION_CREATED = auto()
    VERSION_DELETED = auto()
    NODE_COUNT_CREATED = auto()
    NODE_COUNT_DELETED = auto()
    CPU_COUNT_CREATED = auto()
    CPU_COUNT_DELETED = auto()
    DISK_SIZE_CREATED = auto()
    DISK_SIZE_DELETED = auto()
    DATABASE_ROLE_CREATED = auto()
    DATABASE_ROLE_DELETED = auto()
    DATABASE_OBJECT_CREATED = auto()
    DATABASE_OBJECT_DELETED = auto()
    DB_USER_ROLE_GRANTED = auto()
    DB_USER_PASSWORD_UPDATED = auto()
    DB_USER_ROLE_REVOKED = auto()
    DB_USER_CREATED = auto()
    DB_USER_DELETED = auto()
    REGION_CREATED = auto()
    REGION_DELETED = auto()
    PLAYBOOK_VERSION_CREATED = auto()
    PLAYBOOK_VERSION_DELETED = auto()
    PLAYBOOK_DEFAULT_SET = auto()
    CLUSTER_CREATE_REQUESTED = auto()
    CLUSTER_DELETE_REQUESTED = auto()
    CLUSTER_SCALE_REQUESTED = auto()
    CLUSTER_UPGRADE_REQUESTED = auto()
    CLUSTER_RESTORE_REQUESTED = auto()
    JOB_RESCHEDULE_REQUESTED = auto()


class CPRole(AutoNameStrEnum):
    CP_READONLY = auto()
    CP_USER = auto()
    CP_ADMIN = auto()


class SettingKey(AutoNameStrEnum):
    auth_api_key_signature_ttl_seconds = "auth.api_key_signature_ttl_seconds"
    logging_journald_identifier = "logging.journald_identifier"
    logging_level = "logging.level"
    storage_s3_url = "storage.s3.url"
    storage_s3_admin_access_key = "storage.s3.admin_access_key"
    storage_s3_admin_secret_key = "storage.s3.admin_secret_key"
    storage_s3_default_retention_days = "storage.s3.default_retention_days"
    cluster_default_username = "cluster.default_username"
    cockroach_license_key = "cockroach.license_key"
    cockroach_license_org = "cockroach.license_org"
    observability_prometheus_url = "observability.prometheus_url"
    oidc_cache_ttl_seconds = "oidc.cache_ttl_seconds"
    oidc_enabled = "oidc.enabled"
    oidc_issuer_url = "oidc.issuer_url"
    oidc_client_id = "oidc.client_id"
    oidc_client_secret = "oidc.client_secret"
    oidc_scopes = "oidc.scopes"
    oidc_audience = "oidc.audience"
    oidc_extra_auth_params = "oidc.extra_auth_params"
    oidc_redirect_uri = "oidc.redirect_uri"
    oidc_login_path = "oidc.login_path"
    oidc_session_max_age_seconds = "oidc.session_max_age_seconds"
    oidc_refresh_leeway_seconds = "oidc.refresh_leeway_seconds"
    oidc_cookie_secure = "oidc.cookie_secure"
    oidc_cookie_samesite = "oidc.cookie_samesite"
    oidc_cookie_domain = "oidc.cookie_domain"
    oidc_verify_audience = "oidc.verify_audience"
    oidc_ui_username_claim = "oidc.ui_username_claim"
    oidc_authz_readonly_groups = "oidc.authz_readonly_groups"
    oidc_authz_user_groups = "oidc.authz_user_groups"
    oidc_authz_admin_groups = "oidc.authz_admin_groups"
    oidc_authz_groups_claim = "oidc.authz_groups_claim"


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


class ClusterStatsResponse(BaseModel):
    total: int
    active: int
    creating: int
    unhealthy: int
    failed: int


class JobStatsResponse(BaseModel):
    total: int
    running: int
    queued: int
    failed: int


class ErrorResponse(BaseModel):
    detail: str


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


class ClusterPublic(BaseModel):
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


class Cluster(BaseModel):
    cluster_id: str
    cluster_inventory: List[InventoryRegion]
    lbs_inventory: List[InventoryLB]
    password: bytes | None = None
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


def to_public_cluster(cluster: Cluster) -> ClusterPublic:
    return ClusterPublic.model_validate(cluster.model_dump(exclude={"password"}))


class ExternalConnection(BaseModel):
    cluster_id: str
    name: str
    connection_type: str
    provider: str
    endpoint: str
    bucket_name: str | None = None
    access_key_id: str | None = None
    encrypted_secret_access_key: bytes | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime
    updated_by: str


class ExternalConnectionUpsert(BaseModel):
    cluster_id: str
    name: str
    connection_type: str
    provider: str
    endpoint: str
    bucket_name: str | None = None
    access_key_id: str | None = None
    encrypted_secret_access_key: bytes | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    status: str


class ClusterRequest(BaseModel):
    name: str
    node_count: int
    node_cpus: int
    disk_size: int
    regions: List[str]
    version: str
    group: str


class CommandModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateClusterCommand(CommandModel):
    name: str
    node_count: int
    node_cpus: int
    disk_size: int
    regions: list[str]
    version: str
    group: str


class ClusterUpgradeRequest(CommandModel):
    name: str
    version: str
    auto_finalize: bool


class DeleteClusterCommand(CommandModel):
    cluster_id: str


class DebugClusterCommand(CommandModel):
    pass


class RestoreRequest(CommandModel):
    name: str
    backup_path: str
    restore_aost: str | None
    restore_full_cluster: bool
    object_type: str | None
    object_name: str | None
    backup_into: str | None


class RestoreClusterObjectRequest(CommandModel):
    cluster_id: str
    backup_path: str
    restore_aost: str | None = None
    object_type: Literal["database", "table"]
    object_name: str
    into_db: str | None = None
    new_db_name: str | None = None

    @field_validator(
        "cluster_id",
        "backup_path",
        "object_name",
        "restore_aost",
        "into_db",
        "new_db_name",
        mode="before",
    )
    @classmethod
    def empty_strings_to_none(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                return None
            return stripped
        return value

    @field_validator("object_type", mode="before")
    @classmethod
    def normalize_object_type(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("cluster_id", "backup_path", "object_name")
    @classmethod
    def require_value(cls, value: str | None):
        if value is None:
            raise ValueError("Field must not be empty.")
        return value

    @model_validator(mode="after")
    def validate_restore_options(self):
        if self.object_type == "database" and self.into_db is not None:
            raise ValueError("into_db can only be used when restoring a table.")
        if self.object_type == "table" and self.new_db_name is not None:
            raise ValueError("new_db_name can only be used when restoring a database.")
        return self


class RestoreFullClusterRequest(CommandModel):
    source_cluster_id: str
    target_cluster_id: str
    backup_path: str
    restore_aost: str | None = None

    @field_validator(
        "source_cluster_id",
        "target_cluster_id",
        "backup_path",
        "restore_aost",
        mode="before",
    )
    @classmethod
    def empty_strings_to_none(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                return None
            return stripped
        return value

    @field_validator("source_cluster_id", "target_cluster_id", "backup_path")
    @classmethod
    def require_value(cls, value: str | None):
        if value is None:
            raise ValueError("Field must not be empty.")
        return value


class PollClusterRestoreRequest(CommandModel):
    cluster_id: str
    cp_job_id: int
    cockroach_job_id: int
    poll_attempt: int = 1


class SyncBackupCatalogRequest(CommandModel):
    pass


class SyncClusterBackupCatalogRequest(CommandModel):
    cluster_id: str


class ClusterScaleRequest(CommandModel):
    name: str
    node_count: int
    node_cpus: int
    disk_size: int
    regions: List[str]


class HealthcheckClustersCommand(CommandModel):
    pass


class FailZombieJobsCommand(CommandModel):
    pass


COMMAND_MODELS: dict[CommandType, type[CommandModel]] = {
    CommandType.CREATE_CLUSTER: CreateClusterCommand,
    CommandType.RECREATE_CLUSTER: CreateClusterCommand,
    CommandType.DELETE_CLUSTER: DeleteClusterCommand,
    CommandType.SCALE_CLUSTER: ClusterScaleRequest,
    CommandType.UPGRADE_CLUSTER: ClusterUpgradeRequest,
    CommandType.DEBUG_CLUSTER: DebugClusterCommand,
    CommandType.RESTORE_CLUSTER: RestoreRequest,
    CommandType.RESTORE_CLUSTER_OBJECT: RestoreClusterObjectRequest,
    CommandType.RESTORE_FULL_CLUSTER: RestoreFullClusterRequest,
    CommandType.POLL_CLUSTER_RESTORE: PollClusterRestoreRequest,
    CommandType.SYNC_BACKUP_CATALOG: SyncBackupCatalogRequest,
    CommandType.SYNC_CLUSTER_BACKUP_CATALOG: SyncClusterBackupCatalogRequest,
    CommandType.HEALTHCHECK_CLUSTERS: HealthcheckClustersCommand,
    CommandType.FAIL_ZOMBIE_JOBS: FailZombieJobsCommand,
}


def command_model_for_type(command_type: CommandType) -> type[CommandModel]:
    return COMMAND_MODELS[command_type]


def parse_command_payload(
    command_type: CommandType,
    payload: dict[str, Any] | None,
) -> CommandModel:
    return command_model_for_type(command_type).model_validate(payload or {})


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


class BackupCatalogObject(BaseModel):
    cluster_id: str
    backup_path: str
    ordinal: int
    database_name: str | None = None
    parent_schema_name: str | None = None
    object_name: str | None = None
    object_type: str | None = None
    backup_type: str | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    size_bytes: int | None = None
    row_count: int | None = None
    is_full_cluster: bool | None = None
    regions: str | None = None
    last_seen_at: dt.datetime


class BackupCatalogEntry(BaseModel):
    cluster_id: str
    backup_path: str
    grp: str | None = None
    backup_type: str | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    is_full_cluster: bool = False
    status: str
    object_count: int = 0
    last_seen_at: dt.datetime | None = None
    sync_error: str | None = None
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None


class BackupCatalogSnapshot(BaseModel):
    backups: list[BackupCatalogEntry]


class ClusterRecoveryRestoreApiRequest(BaseModel):
    source_cluster_id: str
    target_cluster_id: str
    backup_path: str
    restore_aost: str | None = None

    @field_validator(
        "source_cluster_id",
        "target_cluster_id",
        "backup_path",
        "restore_aost",
        mode="before",
    )
    @classmethod
    def empty_strings_to_none(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                return None
            return stripped
        return value

    @field_validator("source_cluster_id", "target_cluster_id", "backup_path")
    @classmethod
    def require_value(cls, value: str | None):
        if value is None:
            raise ValueError("Field must not be empty.")
        return value


class BackupCatalogObjectUpsert(BaseModel):
    ordinal: int
    database_name: str | None = None
    parent_schema_name: str | None = None
    object_name: str | None = None
    object_type: str | None = None
    backup_type: str | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    size_bytes: int | None = None
    row_count: int | None = None
    is_full_cluster: bool | None = None
    regions: str | None = None


class BackupCatalogEntryUpsert(BaseModel):
    cluster_id: str
    backup_path: str
    grp: str | None = None
    backup_type: str | None = None
    start_time: dt.datetime | None = None
    end_time: dt.datetime | None = None
    is_full_cluster: bool = False
    status: str = "AVAILABLE"
    object_count: int = 0
    sync_error: str | None = None
    objects: list[BackupCatalogObjectUpsert] = Field(default_factory=list)


class DatabaseUser(BaseModel):
    username: str
    options: list[str] | str | None
    member_of: list[str] | None


class DatabaseRoleTemplateConfig(BaseModel):
    database_role_template: str
    scope_type: str = "schema"
    sql_statement: str = ""


class ClusterDatabaseRole(BaseModel):
    cluster_id: str
    database_name: str
    schema_name: str | None = None
    database_role: str
    database_role_template: str
    scope_type: str
    sql_statement: str


class ClusterDatabaseObject(BaseModel):
    cluster_id: str
    database_name: str
    created_at: dt.datetime
    created_by: str
    updated_at: dt.datetime
    updated_by: str


class CreateClusterDatabaseObjectRequest(BaseModel):
    database_name: str


class NewDatabaseUserRequest(BaseModel):
    username: str
    password: str
    database_roles: list[str] = Field(default_factory=list)


# JOBS


class Msg(BaseModel):
    msg_id: int
    start_after: dt.datetime
    msg_type: CommandType
    msg_data: Dict[str, Any]
    created_at: dt.datetime
    created_by: str


class Job(BaseModel):
    job_id: int
    job_type: CommandType
    status: str
    description: Dict[str, Any]
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
    cluster: ClusterPublic
    metrics: DashboardMetrics


class ClusterJobsSnapshot(BaseModel):
    cluster: ClusterPublic
    jobs: list[Job]


class ClusterUsersSnapshot(BaseModel):
    cluster: ClusterPublic
    database_users: list[DatabaseUser]
    database_role_templates: list[DatabaseRoleTemplateConfig] = Field(default_factory=list)
    database_roles: list[ClusterDatabaseRole] = Field(default_factory=list)


class ClusterBackupsSnapshot(BaseModel):
    cluster: ClusterPublic
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


class ClusterRestoreApiRequest(BaseModel):
    backup_path: str
    restore_aost: str | None = None
    restore_full_cluster: bool
    object_type: str | None = None
    object_name: str | None = None
    backup_into: str | None = None


class ClusterObjectRestoreApiRequest(BaseModel):
    backup_path: str
    restore_aost: str | None = None
    object_type: Literal["database", "table"]
    object_name: str
    into_db: str | None = None
    new_db_name: str | None = None

    @field_validator(
        "backup_path",
        "object_name",
        "restore_aost",
        "into_db",
        "new_db_name",
        mode="before",
    )
    @classmethod
    def empty_strings_to_none(cls, value):
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                return None
            return stripped
        return value

    @field_validator("object_type", mode="before")
    @classmethod
    def normalize_object_type(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("backup_path", "object_name")
    @classmethod
    def require_value(cls, value: str | None):
        if value is None:
            raise ValueError("Field must not be empty.")
        return value

    @model_validator(mode="after")
    def validate_restore_options(self):
        if self.object_type == "database" and self.into_db is not None:
            raise ValueError("into_db can only be used when restoring a table.")
        if self.object_type == "table" and self.new_db_name is not None:
            raise ValueError("new_db_name can only be used when restoring a database.")
        return self


class ClusterDatabaseRolesUpdateRequest(BaseModel):
    database_roles: list[str] = Field(default_factory=list)


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


class OIDCSessionRecord(BaseModel):
    session_id: str
    encrypted_id_token: bytes
    encrypted_refresh_token: bytes | None = None
    token_expires_at: dt.datetime
    session_expires_at: dt.datetime
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None


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


class Alert(BaseModel):
    status: str  # "firing" or "resolved"
    labels: Dict[str, str]
    annotations: Dict[str, str]
    startsAt: dt.datetime
    endsAt: dt.datetime
    fingerprint: str


class AlertmanagerPayload(BaseModel):
    receiver: str
    status: str
    alerts: List[Alert]
    groupLabels: Dict[str, str]
    commonLabels: Dict[str, str]
    commonAnnotations: Dict[str, str]
    externalURL: str


class LiveAlert(BaseModel):
    fingerprint: str
    alert_type: str
    cluster: str | None = None
    nodes: List[str] = Field(default_factory=list)
    summary: str | None = None
    description: str | None = None
    starts_at: dt.datetime
    ends_at: dt.datetime | None = None
