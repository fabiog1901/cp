from abc import ABC, abstractmethod
from typing import Any

from ..models import (
    ApiKeyCreateRequest,
    ApiKeyRecord,
    ApiKeySummary,
    BackupDetails,
    BackupPathOption,
    Cluster,
    ClusterIDRef,
    ClusterOverview,
    CpuCountOption,
    DatabaseUser,
    DiskSizeOption,
    EventLog,
    Job,
    JobID,
    NodeCountOption,
    Nodes,
    Playbook,
    PlaybookOverview,
    Region,
    RegionOption,
    RoleGroupMap,
    Task,
    Version,
    SettingRecord
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
        api_key: ApiKeyCreateRequest,
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
    def get_setting(self, setting_id: str) -> str | None:
        pass

    @abstractmethod
    def update_setting(self, setting_id: str, value: str, updated_by: str) -> None:
        pass

    @abstractmethod
    def reset_setting(self, setting_id: str, updated_by: str) -> None:
        pass

    @abstractmethod
    def get_secret(self, secret_id: str) -> str | None:
        pass

    @abstractmethod
    def list_role_group_mappings(self) -> list[RoleGroupMap]:
        pass

    @abstractmethod
    def list_clusters(
        self,
        groups: list[str],
        is_admin: bool = False,
    ) -> list[ClusterOverview]:
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
    def get_running_clusters(self) -> list[Cluster]:
        pass

    @abstractmethod
    def create_or_update_cluster(
        self,
        cluster_id: str,
        status: str,
        created_by: str,
        grp: str,
        version: str,
        node_cpus: int,
        node_count: int,
        disk_size: int,
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
    ) -> None:
        pass

    @abstractmethod
    def delete_cluster(self, cluster_id: str) -> None:
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
    def get_region_config(self, cloud: str, region: str) -> list[Region]:
        pass

    @abstractmethod
    def add_region(self, region: Region) -> None:
        pass

    @abstractmethod
    def delete_region(self, cloud: str, region: str, zone: str) -> None:
        pass

    @abstractmethod
    def list_versions(self) -> list[Version]:
        pass

    @abstractmethod
    def add_version(self, version: Version) -> None:
        pass

    @abstractmethod
    def remove_version(self, version: str) -> None:
        pass

    @abstractmethod
    def list_upgrade_versions(self, major_version: str) -> list[Version]:
        pass

    @abstractmethod
    def list_node_counts(self) -> list[NodeCountOption]:
        pass

    @abstractmethod
    def list_cpus_per_node(self) -> list[CpuCountOption]:
        pass

    @abstractmethod
    def list_disk_sizes(self) -> list[DiskSizeOption]:
        pass

    @abstractmethod
    def get_nodes(self) -> list[Nodes]:
        pass

    @abstractmethod
    def list_backup_paths(self, dns_address: str) -> list[BackupPathOption]:
        pass

    @abstractmethod
    def list_backup_details(
        self,
        dns_address: str,
        backup_path: str,
    ) -> list[BackupDetails]:
        pass

    @abstractmethod
    def list_database_users(self, dns_address: str) -> list[DatabaseUser]:
        pass

    @abstractmethod
    def create_database_user(
        self,
        dns_address: str,
        username: str,
        password: str,
    ) -> None:
        pass

    @abstractmethod
    def remove_database_user(self, dns_address: str, username: str) -> None:
        pass

    @abstractmethod
    def revoke_database_user_role(
        self,
        dns_address: str,
        username: str,
        role: str,
    ) -> None:
        pass

    @abstractmethod
    def update_database_user_password(
        self,
        dns_address: str,
        username: str,
        password: str,
    ) -> None:
        pass

    @abstractmethod
    def query_prometheus_range(
        self,
        prom_url: str,
        *,
        query: str,
        start: int,
        end: int,
        interval_secs: int,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def list_events(
        self,
        limit: int,
        offset: int,
        groups: list[str] | None = None,
        is_admin: bool = False,
    ) -> list[EventLog]:
        pass

    @abstractmethod
    def get_event_count(self) -> int:
        pass

    @abstractmethod
    def insert_event_log(
        self,
        created_by: str,
        event_type: str,
        event_details: Any = None,
    ) -> None:
        pass

    @abstractmethod
    def list_jobs(self, groups: list[str], is_admin: bool = False) -> list[Job]:
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
    def insert_mapped_job(self, cluster_id: str, job_id: int, status: str) -> None:
        pass

    @abstractmethod
    def update_job(self, job_id: int, status: str) -> None:
        pass

    @abstractmethod
    def fail_zombie_jobs(self) -> list[Any]:
        pass

    @abstractmethod
    def insert_task(
        self,
        job_id: int,
        task_id: int,
        created_at: Any,
        task_name: str,
        task_desc: Any,
    ) -> None:
        pass

    @abstractmethod
    def insert_into_mq(
        self,
        msg_type: str,
        msg_data: dict,
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
    def add_playbook(
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
    def remove_playbook(self, name: str, version: str) -> None:
        pass
