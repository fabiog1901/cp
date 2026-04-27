"""Business logic for admin-managed cluster sizing options."""

from pydantic import ValidationError

from ...infra.errors import RepositoryError
from ...models import (
    AuditEvent,
    CpuCountOption,
    DatabaseRoleTemplateConfig,
    DiskSizeOption,
    NodeCountOption,
)
from ..base import log_event
from ..errors import ServiceValidationError, from_repository_error
from .base import AdminService


class ClusterOptionsService(AdminService):
    def list_node_counts(self) -> list[NodeCountOption]:
        try:
            return self.repo.list_node_counts()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Node counts are temporarily unavailable.",
                fallback_message="Unable to load node counts.",
            ) from err

    def create_node_count(self, node_count: int, created_by: str) -> NodeCountOption:
        try:
            model = NodeCountOption(node_count=node_count)
        except ValidationError as err:
            raise ServiceValidationError("Node count is invalid.") from err

        try:
            self.repo.create_node_count(model)
            log_event(
                self.repo,
                created_by,
                AuditEvent.NODE_COUNT_CREATED,
                {"node_count": model.node_count},
            )
            return model
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Node counts could not be updated right now.",
                conflict_message=f"Node count '{model.node_count}' already exists.",
                validation_message="The node count is invalid.",
                fallback_message=f"Unable to create node count '{model.node_count}'.",
            ) from err

    def delete_node_count(self, node_count: int, deleted_by: str) -> None:
        try:
            self.repo.delete_node_count(node_count)
            log_event(
                self.repo,
                deleted_by,
                AuditEvent.NODE_COUNT_DELETED,
                {"node_count": node_count},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Node counts could not be updated right now.",
                fallback_message=f"Unable to delete node count '{node_count}'.",
            ) from err

    def list_cpu_counts(self) -> list[CpuCountOption]:
        try:
            return self.repo.list_cpus_per_node()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="CPU counts are temporarily unavailable.",
                fallback_message="Unable to load CPU counts.",
            ) from err

    def create_cpu_count(self, cpu_count: int, created_by: str) -> CpuCountOption:
        try:
            model = CpuCountOption(cpu_count=cpu_count)
        except ValidationError as err:
            raise ServiceValidationError("CPU count is invalid.") from err

        try:
            self.repo.create_cpu_count(model)
            log_event(
                self.repo,
                created_by,
                AuditEvent.CPU_COUNT_CREATED,
                {"cpu_count": model.cpu_count},
            )
            return model
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="CPU counts could not be updated right now.",
                conflict_message=f"CPU count '{model.cpu_count}' already exists.",
                validation_message="The CPU count is invalid.",
                fallback_message=f"Unable to create CPU count '{model.cpu_count}'.",
            ) from err

    def delete_cpu_count(self, cpu_count: int, deleted_by: str) -> None:
        try:
            self.repo.delete_cpu_count(cpu_count)
            log_event(
                self.repo,
                deleted_by,
                AuditEvent.CPU_COUNT_DELETED,
                {"cpu_count": cpu_count},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="CPU counts could not be updated right now.",
                fallback_message=f"Unable to delete CPU count '{cpu_count}'.",
            ) from err

    def list_disk_sizes(self) -> list[DiskSizeOption]:
        try:
            return self.repo.list_disk_sizes()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Disk sizes are temporarily unavailable.",
                fallback_message="Unable to load disk sizes.",
            ) from err

    def create_disk_size(self, size_gb: int, created_by: str) -> DiskSizeOption:
        try:
            model = DiskSizeOption(size_gb=size_gb)
        except ValidationError as err:
            raise ServiceValidationError("Disk size is invalid.") from err

        try:
            self.repo.create_disk_size(model)
            log_event(
                self.repo,
                created_by,
                AuditEvent.DISK_SIZE_CREATED,
                {"size_gb": model.size_gb},
            )
            return model
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Disk sizes could not be updated right now.",
                conflict_message=f"Disk size '{model.size_gb}' already exists.",
                validation_message="The disk size is invalid.",
                fallback_message=f"Unable to create disk size '{model.size_gb}'.",
            ) from err

    def delete_disk_size(self, size_gb: int, deleted_by: str) -> None:
        try:
            self.repo.delete_disk_size(size_gb)
            log_event(
                self.repo,
                deleted_by,
                AuditEvent.DISK_SIZE_DELETED,
                {"size_gb": size_gb},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Disk sizes could not be updated right now.",
                fallback_message=f"Unable to delete disk size '{size_gb}'.",
            ) from err

    def list_database_role_templates(self) -> list[DatabaseRoleTemplateConfig]:
        try:
            return self.repo.list_database_role_templates()
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database role templates are temporarily unavailable.",
                fallback_message="Unable to load database role templates.",
            ) from err

    def create_database_role_template(
        self,
        database_role_template: str,
        scope_type: str,
        sql_statement: str,
        created_by: str,
    ) -> DatabaseRoleTemplateConfig:
        try:
            model = DatabaseRoleTemplateConfig(
                database_role_template=self._normalize_database_role_template(
                    database_role_template
                ),
                scope_type=self._normalize_database_role_scope(scope_type),
                sql_statement=self._normalize_database_role_sql(
                    sql_statement,
                ),
            )
        except ValidationError as err:
            raise ServiceValidationError(
                "Database role template configuration is invalid."
            ) from err

        try:
            self.repo.create_database_role_template(model)
            log_event(
                self.repo,
                created_by,
                AuditEvent.DATABASE_ROLE_CREATED,
                {"database_role_template": model.database_role_template},
            )
            return model
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database role templates could not be updated right now.",
                conflict_message=f"Database role template '{model.database_role_template}' already exists.",
                validation_message="The database role template configuration is invalid.",
                fallback_message=f"Unable to create database role template '{model.database_role_template}'.",
            ) from err

    def delete_database_role_template(
        self, database_role_template: str, deleted_by: str
    ) -> None:
        normalized_database_role_template = self._normalize_database_role_template(
            database_role_template
        )
        try:
            self.repo.delete_database_role_template(normalized_database_role_template)
            log_event(
                self.repo,
                deleted_by,
                AuditEvent.DATABASE_ROLE_DELETED,
                {"database_role_template": normalized_database_role_template},
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Database role templates could not be updated right now.",
                fallback_message=f"Unable to delete database role template '{normalized_database_role_template}'.",
            ) from err

    @staticmethod
    def _normalize_database_role_template(database_role_template: str) -> str:
        normalized = str(database_role_template or "").strip()
        if not normalized:
            raise ServiceValidationError("Database role template is required.")
        return normalized

    @staticmethod
    def _normalize_database_role_scope(scope_type: str) -> str:
        normalized = str(scope_type or "schema").strip().lower()
        if normalized not in {"database", "schema"}:
            raise ServiceValidationError(
                "Database role template scope must be 'database' or 'schema'."
            )
        return normalized

    @staticmethod
    def _normalize_database_role_sql(
        sql_statement: str,
    ) -> str:
        normalized = str(sql_statement or "").strip()
        if normalized:
            return normalized
        return "CREATE ROLE IF NOT EXISTS {database_role};"
