<!-- GENERATED FILE: DO NOT EDIT -->

# Generated Package Index

| Package | Modules | Classes | Functions | Routes |
| --- | ---: | ---: | ---: | ---: |
| `cp` | 87 | 165 | 153 | 75 |
| `tools` | 1 | 5 | 31 | 0 |

## Modules

| Module | Path | Summary |
| --- | --- | --- |
| `cp` | `cp/__init__.py` | _No docstring._ |
| `cp.api` | `cp/api/__init__.py` | FastAPI router packages for the cp application. |
| `cp.api.admin` | `cp/api/admin/__init__.py` | _No docstring._ |
| `cp.api.admin.api_keys` | `cp/api/admin/api_keys.py` | _No docstring._ |
| `cp.api.admin.common` | `cp/api/admin/common.py` | _No docstring._ |
| `cp.api.admin.cpu_counts` | `cp/api/admin/cpu_counts.py` | _No docstring._ |
| `cp.api.admin.database_role_templates` | `cp/api/admin/database_role_templates.py` | _No docstring._ |
| `cp.api.admin.disk_sizes` | `cp/api/admin/disk_sizes.py` | _No docstring._ |
| `cp.api.admin.node_counts` | `cp/api/admin/node_counts.py` | _No docstring._ |
| `cp.api.admin.playbooks` | `cp/api/admin/playbooks.py` | _No docstring._ |
| `cp.api.admin.regions` | `cp/api/admin/regions.py` | _No docstring._ |
| `cp.api.admin.settings` | `cp/api/admin/settings.py` | _No docstring._ |
| `cp.api.admin.versions` | `cp/api/admin/versions.py` | _No docstring._ |
| `cp.api.alerts` | `cp/api/alerts.py` | Alert API routes. |
| `cp.api.cluster_recovery` | `cp/api/cluster_recovery.py` | Cluster recovery API routes. |
| `cp.api.clusters` | `cp/api/clusters.py` | Cluster API routes. |
| `cp.api.events` | `cp/api/events.py` | Event API routes. |
| `cp.api.jobs` | `cp/api/jobs.py` | Job API routes. |
| `cp.auth` | `cp/auth/__init__.py` | _No docstring._ |
| `cp.auth.common` | `cp/auth/common.py` | Shared authentication primitives. |
| `cp.auth.dependencies` | `cp/auth/dependencies.py` | Authentication and authorization dependencies. |
| `cp.auth.oidc` | `cp/auth/oidc.py` | OIDC client helpers. |
| `cp.auth.router` | `cp/auth/router.py` | Authentication HTTP routes. |
| `cp.infra` | `cp/infra/__init__.py` | Shared infrastructure entrypoints for DB lifecycle and FastAPI dependencies. |
| `cp.infra.db` | `cp/infra/db.py` | Low-level CP metadata database infrastructure. |
| `cp.infra.dependencies` | `cp/infra/dependencies.py` | _No docstring._ |
| `cp.infra.errors` | `cp/infra/errors.py` | Infrastructure-layer exception types. |
| `cp.infra.logging` | `cp/infra/logging.py` | Logging configuration for operational messages. |
| `cp.infra.util` | `cp/infra/util.py` | Shared operational utilities. |
| `cp.main` | `cp/main.py` | FastAPI application entry point. |
| `cp.models` | `cp/models.py` | Shared CP domain, API, command, and persistence models. |
| `cp.repos` | `cp/repos/__init__.py` | Repository-layer package. |
| `cp.repos.admin` | `cp/repos/admin/__init__.py` | Admin repository package. |
| `cp.repos.admin.api_keys` | `cp/repos/admin/api_keys.py` | Admin API keys repository. |
| `cp.repos.admin.base` | `cp/repos/admin/base.py` | Shared base for admin-oriented repositories. |
| `cp.repos.admin.cluster_options` | `cp/repos/admin/cluster_options.py` | Admin option and cluster database-access metadata repository. |
| `cp.repos.admin.playbooks` | `cp/repos/admin/playbooks.py` | Admin playbooks repository. |
| `cp.repos.admin.regions` | `cp/repos/admin/regions.py` | Admin regions repository. |
| `cp.repos.admin.settings` | `cp/repos/admin/settings.py` | Admin settings repository. |
| `cp.repos.admin.versions` | `cp/repos/admin/versions.py` | Admin versions repository. |
| `cp.repos.alerts` | `cp/repos/alerts.py` | Alerts repository. |
| `cp.repos.auth` | `cp/repos/auth.py` | Auth/support repository. |
| `cp.repos.backup_catalog` | `cp/repos/backup_catalog.py` | Backup catalog metadata repository. |
| `cp.repos.cluster` | `cp/repos/cluster.py` | Cluster metadata repository. |
| `cp.repos.cluster_jobs` | `cp/repos/cluster_jobs.py` | Cluster jobs repository. |
| `cp.repos.common` | `cp/repos/common.py` | Shared helpers for repository models. |
| `cp.repos.event` | `cp/repos/event.py` | Event repository. |
| `cp.repos.external_connections` | `cp/repos/external_connections.py` | External connections repository. |
| `cp.repos.jobs` | `cp/repos/jobs.py` | Job and task metadata repository. |
| `cp.repos.mq` | `cp/repos/mq.py` | Message queue repository. |
| `cp.services` | `cp/services/__init__.py` | Service-layer package. |
| `cp.services.admin` | `cp/services/admin/__init__.py` | Admin service package. |
| `cp.services.admin.api_keys` | `cp/services/admin/api_keys.py` | Admin API key service. |
| `cp.services.admin.base` | `cp/services/admin/base.py` | Shared base for admin-facing services. |
| `cp.services.admin.cluster_options` | `cp/services/admin/cluster_options.py` | Admin cluster option service. |
| `cp.services.admin.playbooks` | `cp/services/admin/playbooks.py` | Admin playbook service. |
| `cp.services.admin.regions` | `cp/services/admin/regions.py` | Business logic for the admin regions vertical. |
| `cp.services.admin.settings` | `cp/services/admin/settings.py` | Business logic for the admin settings vertical. |
| `cp.services.admin.versions` | `cp/services/admin/versions.py` | Business logic for the admin versions vertical. |
| `cp.services.alerts` | `cp/services/alerts.py` | Business logic for the alerts vertical. |
| `cp.services.auth` | `cp/services/auth.py` | Business logic for auth-related shared operations. |
| `cp.services.backup_catalog` | `cp/services/backup_catalog.py` | Backup catalog service. |
| `cp.services.base` | `cp/services/base.py` | Shared service-layer helpers. |
| `cp.services.cluster` | `cp/services/cluster.py` | Cluster lifecycle service. |
| `cp.services.cluster_backups` | `cp/services/cluster_backups.py` | Backup and restore service for individual clusters. |
| `cp.services.cluster_db` | `cp/services/cluster_db.py` | Shared helpers for connecting to a cluster SQL endpoint. |
| `cp.services.cluster_jobs` | `cp/services/cluster_jobs.py` | Business logic for the cluster jobs vertical. |
| `cp.services.cluster_users` | `cp/services/cluster_users.py` | Database access workflows for managed clusters. |
| `cp.services.dashboard` | `cp/services/dashboard.py` | Cluster dashboard service. |
| `cp.services.errors` | `cp/services/errors.py` | Service-layer exception types and repository error translation. |
| `cp.services.events` | `cp/services/events.py` | Business logic for the events vertical. |
| `cp.services.jobs` | `cp/services/jobs.py` | Business logic for the jobs vertical. |
| `cp.services.storage_broker` | `cp/services/storage_broker.py` | Provision and resolve external storage connections for clusters. |
| `cp.workers` | `cp/workers/__init__.py` | Worker runtime package. |
| `cp.workers.local` | `cp/workers/local/__init__.py` | Local CP workers that use CP-managed resources and SQL connections. |
| `cp.workers.local.backup_catalog` | `cp/workers/local/backup_catalog.py` | Local backup catalog worker. |
| `cp.workers.local.restore` | `cp/workers/local/restore.py` | Local restore worker. |
| `cp.workers.queue` | `cp/workers/queue.py` | Queue worker entry point. |
| `cp.workers.remote` | `cp/workers/remote/__init__.py` | Remote workers that execute Ansible playbooks over SSH. |
| `cp.workers.remote.ansible` | `cp/workers/remote/ansible.py` | Shared Ansible runner helpers for remote workers. |
| `cp.workers.remote.common` | `cp/workers/remote/common.py` | Shared helpers for cluster workers. |
| `cp.workers.remote.create` | `cp/workers/remote/create.py` | Remote cluster creation worker. |
| `cp.workers.remote.debug_zip` | `cp/workers/remote/debug_zip.py` | Remote cluster debug zip worker. |
| `cp.workers.remote.delete` | `cp/workers/remote/delete.py` | Remote cluster deletion worker. |
| `cp.workers.remote.healthcheck` | `cp/workers/remote/healthcheck.py` | Remote cluster healthcheck worker. |
| `cp.workers.remote.scale` | `cp/workers/remote/scale.py` | Remote cluster scale worker. |
| `cp.workers.remote.upgrade` | `cp/workers/remote/upgrade.py` | Remote cluster upgrade worker. |
| `tools.docsync` | `tools/docsync.py` | Generate deterministic documentation indexes from the CP codebase. |
