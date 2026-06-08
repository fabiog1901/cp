<!-- GENERATED FILE: DO NOT EDIT -->

# Generated Package Index

| Package | Modules | Classes | Functions | Routes |
| --- | ---: | ---: | ---: | ---: |
| `cp` | 63 | 112 | 97 | 54 |
| `tools` | 1 | 5 | 32 | 0 |

## Modules

| Module | Path | Summary |
| --- | --- | --- |
| `cp` | `cp/__init__.py` | _No docstring._ |
| `cp.api` | `cp/api/__init__.py` | FastAPI router packages for the cp application. |
| `cp.api.admin` | `cp/api/admin/__init__.py` | _No docstring._ |
| `cp.api.admin.cpu_counts` | `cp/api/admin/cpu_counts.py` | _No docstring._ |
| `cp.api.admin.database_role_templates` | `cp/api/admin/database_role_templates.py` | _No docstring._ |
| `cp.api.admin.disk_sizes` | `cp/api/admin/disk_sizes.py` | _No docstring._ |
| `cp.api.admin.node_counts` | `cp/api/admin/node_counts.py` | _No docstring._ |
| `cp.api.admin.regions` | `cp/api/admin/regions.py` | _No docstring._ |
| `cp.api.admin.versions` | `cp/api/admin/versions.py` | _No docstring._ |
| `cp.api.alerts` | `cp/api/alerts.py` | Alert API routes. |
| `cp.api.cluster_recovery` | `cp/api/cluster_recovery.py` | Cluster recovery API routes. |
| `cp.api.clusters` | `cp/api/clusters.py` | Cluster API routes. |
| `cp.audit` | `cp/audit.py` | CP-specific audit record construction helpers. |
| `cp.cluster_database` | `cp/cluster_database.py` | Managed-cluster database connection helpers. |
| `cp.cpkit_integration` | `cp/cpkit_integration.py` | CP wiring for cpkit-provided capabilities. |
| `cp.main` | `cp/main.py` | CP FastAPI application wiring. |
| `cp.models` | `cp/models.py` | Shared CP domain, API, command, and persistence models. |
| `cp.prometheus` | `cp/prometheus.py` | Prometheus scrape target helpers. |
| `cp.repos` | `cp/repos/__init__.py` | Repository-layer package. |
| `cp.repos.admin` | `cp/repos/admin/__init__.py` | Admin repository package. |
| `cp.repos.admin.base` | `cp/repos/admin/base.py` | Shared base for admin-oriented repositories. |
| `cp.repos.admin.cluster_options` | `cp/repos/admin/cluster_options.py` | Admin option and cluster database-access metadata repository. |
| `cp.repos.admin.regions` | `cp/repos/admin/regions.py` | Admin regions repository. |
| `cp.repos.admin.versions` | `cp/repos/admin/versions.py` | Admin versions repository. |
| `cp.repos.alerts` | `cp/repos/alerts.py` | Alerts repository. |
| `cp.repos.backup_catalog` | `cp/repos/backup_catalog.py` | Backup catalog metadata repository. |
| `cp.repos.cluster` | `cp/repos/cluster.py` | Cluster metadata repository. |
| `cp.repos.cluster_artifacts` | `cp/repos/cluster_artifacts.py` | Cluster artifact catalog repository. |
| `cp.repos.cluster_jobs` | `cp/repos/cluster_jobs.py` | Cluster jobs repository. |
| `cp.repos.common` | `cp/repos/common.py` | Shared helpers for repository models. |
| `cp.repos.external_connections` | `cp/repos/external_connections.py` | External connections repository. |
| `cp.repository` | `cp/repository.py` | CP repository factory and application-specific database error handling. |
| `cp.services` | `cp/services/__init__.py` | Service-layer package. |
| `cp.services.admin` | `cp/services/admin/__init__.py` | Admin service package. |
| `cp.services.admin.base` | `cp/services/admin/base.py` | Shared base for admin-facing services. |
| `cp.services.admin.cluster_options` | `cp/services/admin/cluster_options.py` | Admin cluster option service. |
| `cp.services.admin.regions` | `cp/services/admin/regions.py` | Business logic for the admin regions vertical. |
| `cp.services.admin.versions` | `cp/services/admin/versions.py` | Business logic for the admin versions vertical. |
| `cp.services.alerts` | `cp/services/alerts.py` | Business logic for the alerts vertical. |
| `cp.services.backup_catalog` | `cp/services/backup_catalog.py` | Backup catalog service. |
| `cp.services.base` | `cp/services/base.py` | Shared service-layer helpers. |
| `cp.services.cluster` | `cp/services/cluster.py` | Cluster lifecycle service. |
| `cp.services.cluster_backups` | `cp/services/cluster_backups.py` | Backup and restore service for individual clusters. |
| `cp.services.cluster_db` | `cp/services/cluster_db.py` | Shared helpers for connecting to a cluster SQL endpoint. |
| `cp.services.cluster_jobs` | `cp/services/cluster_jobs.py` | Business logic for the cluster jobs vertical. |
| `cp.services.cluster_users` | `cp/services/cluster_users.py` | Database access workflows for managed clusters. |
| `cp.services.dashboard` | `cp/services/dashboard.py` | Cluster dashboard service. |
| `cp.services.errors` | `cp/services/errors.py` | Compatibility exports for service-layer exception types. |
| `cp.services.storage_broker` | `cp/services/storage_broker.py` | Provision and resolve external storage connections for clusters. |
| `cp.workers` | `cp/workers/__init__.py` | Worker runtime package. |
| `cp.workers.commands` | `cp/workers/commands.py` | CP command handlers for queued framework jobs. |
| `cp.workers.local` | `cp/workers/local/__init__.py` | Local CP workers that use CP-managed resources and SQL connections. |
| `cp.workers.local.backup_catalog` | `cp/workers/local/backup_catalog.py` | Local backup catalog worker. |
| `cp.workers.local.restore` | `cp/workers/local/restore.py` | Local restore worker. |
| `cp.workers.remote` | `cp/workers/remote/__init__.py` | Remote workers that prepare CP inputs for cpkit playbook execution. |
| `cp.workers.remote.common` | `cp/workers/remote/common.py` | Shared helpers for cluster workers. |
| `cp.workers.remote.create` | `cp/workers/remote/create.py` | Remote cluster creation worker. |
| `cp.workers.remote.debug_zip` | `cp/workers/remote/debug_zip.py` | Remote cluster debug zip worker. |
| `cp.workers.remote.delete` | `cp/workers/remote/delete.py` | Remote cluster deletion worker. |
| `cp.workers.remote.healthcheck` | `cp/workers/remote/healthcheck.py` | Remote cluster healthcheck worker. |
| `cp.workers.remote.poll_debug_zip` | `cp/workers/remote/poll_debug_zip.py` | Remote debug zip polling worker. |
| `cp.workers.remote.scale` | `cp/workers/remote/scale.py` | Remote cluster scale worker. |
| `cp.workers.remote.upgrade` | `cp/workers/remote/upgrade.py` | Remote cluster upgrade worker. |
| `tools.docsync` | `tools/docsync.py` | Generate deterministic documentation indexes from the CP codebase. |
