from abc import ABC, abstractmethod
from typing import Any

from ..models import (
    ApiKeyCreateRequestInDB,
    ApiKeyRecord,
    ApiKeySummary,
    Cluster,
    ClusterIDRef,
    ClusterOverview,
    ClusterStatsResponse,
    CommandModel,
    CommandType,
    CpuCountOption,
    DiskSizeOption,
    ExternalConnection,
    ExternalConnectionUpsert,
    Job,
    JobID,
    JobStatsResponse,
    LiveAlert,
    LogMsg,
    NodeCountOption,
    Nodes,
    OIDCSessionRecord,
    Playbook,
    PlaybookOverview,
    Region,
    RegionOption,
    RoleGroupMap,
    SettingKey,
    SettingRecord,
    Task,
    Version,
)


class BaseRepo(ABC):
    @abstractmethod
    def get_api_key(self, access_key: str) -> ApiKeyRecord | None:
        pass

    @abstractmethod
    def list_api_keys(self, access_key: str | None = None) -> list[ApiKeySummary]:
        pass

    @abstractmethod
    def create_api_key(
        self,
        api_key: ApiKeyCreateRequestInDB,
        *,
        owner: str,
        encrypted_secret_access_key: bytes,
    ) -> ApiKeySummary:
        pass

    @abstractmethod
    def delete_api_key(self, access_key: str) -> None:
        pass

    @abstractmethod
    def list_settings(self) -> list[SettingRecord]:
        pass

    @abstractmethod
    def get_setting(self, setting_key: SettingKey) -> SettingRecord | None:
        pass

    @abstractmethod
    def update_setting(
        self, setting_key: SettingKey, value: str, updated_by: str
    ) -> None:
        pass

    @abstractmethod
    def reset_setting(self, setting_key: SettingKey, updated_by: str) -> None:
        pass

    @abstractmethod
    def list_role_group_mappings(self) -> list[RoleGroupMap]:
        pass

    @abstractmethod
    def get_oidc_session(self, session_id: str) -> OIDCSessionRecord | None:
        pass

    @abstractmethod
    def create_oidc_session(self, session: OIDCSessionRecord) -> None:
        pass

    @abstractmethod
    def update_oidc_session(
        self,
        session_id: str,
        *,
        encrypted_id_token: bytes,
        encrypted_refresh_token: bytes | None,
        token_expires_at,
    ) -> None:
        pass

    @abstractmethod
    def delete_oidc_session(self, session_id: str) -> None:
        pass

    @abstractmethod
    def list_clusters(
        self,
        groups: list[str],
        is_admin: bool = False,
    ) -> list[ClusterOverview]:
        pass

    @abstractmethod
    def get_cluster_stats(
        self,
        groups: list[str],
        is_admin: bool = False,
    ) -> ClusterStatsResponse:
        pass

    @abstractmethod
    def get_cluster(
        self,
        cluster_id: str,
        groups: list[str],
        is_admin: bool = False,
    ) -> Cluster | None:
        pass

    @abstractmethod
    def list_active_clusters(self) -> list[Cluster]:
        pass

    @abstractmethod
    def upsert_cluster(
        self,
        cluster_id: str,
        status: str,
        created_by: str,
        grp: str,
        version: str,
        node_cpus: int,
        node_count: int,
        disk_size: int,
        password: bytes | None = None,
    ) -> None:
        pass

    @abstractmethod
    def update_cluster(
        self,
        cluster_id: str,
        updated_by: str,
        cluster_inventory: list[Any] | None = None,
        lbs_inventory: list[Any] | None = None,
        version: str | None = None,
        node_count: int | None = None,
        node_cpus: int | None = None,
        disk_size: int | None = None,
        status: str | None = None,
        grp: str | None = None,
        password: bytes | None = None,
    ) -> None:
        pass

    @abstractmethod
    def delete_cluster(self, cluster_id: str) -> None:
        pass

    @abstractmethod
    def list_external_connections(self, cluster_id: str) -> list[ExternalConnection]:
        pass

    @abstractmethod
    def get_external_connection(
        self,
        cluster_id: str,
        name: str,
    ) -> ExternalConnection | None:
        pass

    @abstractmethod
    def upsert_external_connection(
        self,
        connection: ExternalConnectionUpsert,
        updated_by: str,
    ) -> None:
        pass

    @abstractmethod
    def delete_external_connection(self, cluster_id: str, name: str) -> None:
        pass

    @abstractmethod
    def list_cluster_jobs(self, cluster_id: str) -> list[Job]:
        pass

    @abstractmethod
    def list_regions(self) -> list[Region]:
        pass

    @abstractmethod
    def list_region_options(self) -> list[RegionOption]:
        pass

    @abstractmethod
    def list_region_config(self, cloud: str, region: str) -> list[Region]:
        pass

    @abstractmethod
    def create_region(self, region: Region) -> None:
        pass

    @abstractmethod
    def delete_region(self, cloud: str, region: str, zone: str) -> None:
        pass

    @abstractmethod
    def list_versions(self) -> list[Version]:
        pass

    @abstractmethod
    def create_version(self, version: Version) -> None:
        pass

    @abstractmethod
    def delete_version(self, version: str) -> None:
        pass

    @abstractmethod
    def list_upgrade_versions(self, major_version: str) -> list[Version]:
        pass

    @abstractmethod
    def list_node_counts(self) -> list[NodeCountOption]:
        pass

    @abstractmethod
    def create_node_count(self, node_count: NodeCountOption) -> None:
        pass

    @abstractmethod
    def delete_node_count(self, node_count: int) -> None:
        pass

    @abstractmethod
    def list_cpus_per_node(self) -> list[CpuCountOption]:
        pass

    @abstractmethod
    def create_cpu_count(self, cpu_count: CpuCountOption) -> None:
        pass

    @abstractmethod
    def delete_cpu_count(self, cpu_count: int) -> None:
        pass

    @abstractmethod
    def list_disk_sizes(self) -> list[DiskSizeOption]:
        pass

    @abstractmethod
    def create_disk_size(self, disk_size: DiskSizeOption) -> None:
        pass

    @abstractmethod
    def delete_disk_size(self, size_gb: int) -> None:
        pass

    @abstractmethod
    def list_cluster_nodes(self) -> list[Nodes]:
        pass

    @abstractmethod
    def list_jobs(self, groups: list[str], is_admin: bool = False) -> list[Job]:
        pass

    @abstractmethod
    def get_job_stats(
        self,
        groups: list[str],
        is_admin: bool = False,
    ) -> JobStatsResponse:
        pass

    @abstractmethod
    def get_job(
        self,
        job_id: int,
        groups: list[str],
        is_admin: bool = False,
    ) -> Job | None:
        pass

    @abstractmethod
    def list_tasks(self, job_id: int) -> list[Task]:
        pass

    @abstractmethod
    def list_linked_clusters(self, job_id: int) -> list[ClusterIDRef]:
        pass

    @abstractmethod
    def link_job_to_cluster(self, cluster_id: str, job_id: int, status: str) -> None:
        pass

    @abstractmethod
    def update_job(self, job_id: int, status: str) -> None:
        pass

    @abstractmethod
    def fail_zombie_jobs(self) -> list[Any]:
        pass

    @abstractmethod
    def create_task(
        self,
        job_id: int,
        task_id: int,
        created_at: Any,
        task_name: str,
        task_desc: Any,
    ) -> None:
        pass

    @abstractmethod
    def enqueue_command(
        self,
        command_type: CommandType,
        payload: CommandModel,
        created_by: str,
    ) -> JobID:
        pass

    @abstractmethod
    def get_playbook(self, name: str, version: str) -> Playbook | None:
        pass

    @abstractmethod
    def get_default_playbook(self, name: str) -> Playbook | None:
        pass

    @abstractmethod
    def list_playbook_versions(self, name: str) -> list[PlaybookOverview]:
        pass

    @abstractmethod
    def create_playbook(
        self,
        name: str,
        playbook: bytes,
        created_by: str,
    ) -> PlaybookOverview | None:
        pass

    @abstractmethod
    def set_default_playbook(self, name: str, version: str, updated_by: str) -> None:
        pass

    @abstractmethod
    def delete_playbook(self, name: str, version: str) -> None:
        pass

    #
    # EVENTS
    #
    @abstractmethod
    def list_events(
        self,
        limit: int,
        offset: int,
        groups: list[str] | None = None,
        is_admin: bool = False,
    ) -> list[LogMsg]:
        pass

    @abstractmethod
    def get_event_count(self) -> int:
        pass

    @abstractmethod
    def log_event(self, event: LogMsg) -> None:
        pass

    #
    # ALERTS
    #
    @abstractmethod
    def list_live_alerts(self) -> list[LiveAlert]:
        pass

    @abstractmethod
    def upsert_live_alert(self, alert: LiveAlert) -> None:
        pass
