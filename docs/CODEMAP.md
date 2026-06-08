# CP Code Map

This file is a navigation index for humans and coding agents. Use it to find the
right layer and domain before reading implementation details.

## System Shape

CP is a FastAPI control plane with a single-page web UI. It stores control-plane
metadata in the CP database, executes some SQL directly against managed
CockroachDB clusters, and delegates longer cluster lifecycle work to queued
worker/playbook flows.

The main backend flow is:

1. `cp/api/` receives HTTP requests and enforces auth dependencies.
2. `cp/services/` owns business workflows and side effects.
3. `cp/repos/` reads and writes CP metadata tables.
4. `cp/workers/` executes queued or background cluster operations.
5. `webapp/` calls the API and shapes data for the browser UI.

Keep route handlers thin, keep business decisions in services, and keep repos
limited to persistence.

## Top-Level Directories

| Path | Purpose |
| --- | --- |
| `cp/api/` | FastAPI routers. Converts HTTP/auth context into service calls. |
| `cp/api/admin/` | Admin option CRUD endpoints such as versions, regions, role templates, and playbooks. |
| `cp/auth.py` | CP-specific cpkit OIDC wiring and exported auth dependencies. |
| `cp/infra/` | Cross-cutting infrastructure: DB connection helpers, dependency factories, logging, errors, cluster connection utilities. |
| `cp/repos/` | CP metadata persistence. Repos should not execute SQL against managed clusters. |
| `cp/repos/admin/` | Persistence for admin-configured options and cluster database access metadata. |
| `cp/services/` | Business workflows. Coordinates repos, managed-cluster SQL, audit events, and workers. |
| `cp/services/admin/` | Business logic for admin option CRUD. |
| `cp/workers/` | Queue handlers and local/remote worker operations. |
| `resources/` | CP schema and seed/dev SQL plus playbook examples. |
| `webapp/` | Browser UI: HTML, CSS, Alpine state, routing, and API calls. |

## Core Files

| Path | Why it matters |
| --- | --- |
| `cp/main.py` | CP router/hook/worker contribution to `cpkit.create_cpkit_app`. |
| `cp/repository.py` | App repository factory and app-specific database error translation. |
| `cp/cluster_database.py` | Managed-cluster SQL connection helper. |
| `cp/models.py` | Pydantic models, enums, command payloads, and API response shapes. |
| `cp/infra/dependencies.py` | Service/repo dependency factories used by API routes. |
| `cp/repos/__init__.py` | Composes repo mixins into the concrete `Repo` class. |
| `resources/cpkit_ddl.sql` | Framework-owned schema and tables. |
| `resources/ddl.sql` | Canonical CP metadata schema. |
| `webapp/index.html` | UI layout and Alpine template bindings. |
| `webapp/script.js` | UI state, hash routing, API calls, and client-side data shaping. |
| `webapp/style.css` | UI styling and layout behavior. |

## Layer Rules

### API Layer

Files under `cp/api/` should:

- define routes and response models;
- call `get_access_scope`, `require_user`, `require_readonly`, and audit actor dependencies;
- delegate behavior to services;
- translate `ServiceError` into HTTP errors.

They should not contain domain workflows, CP database queries, or managed-cluster
SQL.

### Service Layer

Files under `cp/services/` should:

- own domain workflows and validations;
- coordinate CP metadata repos;
- execute managed-cluster SQL only through cluster connection helpers;
- write audit events for user-visible changes;
- translate repository and cluster SQL failures into service errors.

### Repository Layer

Files under `cp/repos/` should:

- query or mutate CP metadata tables;
- return typed models;
- avoid business decisions and audit logging;
- avoid direct SQL against managed CockroachDB clusters.

### Webapp Layer

Files under `webapp/` should:

- own client routing, UI state, and browser interaction;
- call API endpoints explicitly;
- perform view-specific data shaping only when it is UI presentation work;
- avoid encoding backend business rules that should live in services.

## Major Domains

### Cluster Lifecycle

Use this area for creating, deleting, scaling, upgrading, debugging, and health
checking clusters.

| Concern | Entry points |
| --- | --- |
| API | `cp/api/clusters.py`, `cp/api/jobs.py` |
| Services | `cp/services/cluster.py`, `cp/services/cluster_jobs.py`, `cp/services/jobs.py` |
| Repos | `cp/repos/cluster.py`, `cp/repos/cluster_jobs.py`, `cp/repos/jobs.py`, `cp/repos/mq.py` |
| Workers | `cp/workers/queue.py`, `cp/workers/remote/*.py` |
| Models | `Cluster*`, `Command*`, `Job*` in `cp/models.py` |
| UI | Cluster detail/dashboard sections in `webapp/index.html` and `webapp/script.js` |

Typical flow:

1. API receives a cluster operation request.
2. Service validates access/state and enqueues a job/command.
3. Worker consumes the command and runs local or remote automation.
4. Job/task state is persisted and surfaced to the UI.

### Database Access Management

This is the densest current domain. It covers managed database objects, generated
database roles, database users, direct user-role grants, and IdP group-to-role
mappings.

| Concern | Entry points |
| --- | --- |
| API | `cp/api/clusters.py` |
| Service | `cp/services/cluster_users.py` |
| Repo | `cp/repos/admin/cluster_options.py` |
| Schema | `resources/ddl.sql` |
| Models | `DatabaseUser`, `ClusterDatabaseObject*`, `ClusterDatabaseRole*` in `cp/models.py` |
| UI | Database Management and User Management sections in `webapp/index.html` and `webapp/script.js` |

Important tables:

- `database_role_templates`: admin-defined templates for generated roles.
- `cluster_database_objects`: databases managed by CP per cluster.
- `cluster_database_roles`: generated roles materialized from templates.
- `cluster_database_role_group_mappings`: CP-stored desired mapping from IdP groups to generated database roles.

Important API resources:

- `GET/POST /clusters/{cluster_id}/database-objects`
- `GET/DELETE /clusters/{cluster_id}/database-objects/{database_name}`
- `GET /clusters/{cluster_id}/database-role-group-mappings`
- `PUT /clusters/{cluster_id}/database-role-group-mappings/{database_role}`
- `GET/POST /clusters/{cluster_id}/users`
- user password and direct role grant/revoke routes under `/clusters/{cluster_id}/users/...`

Key design notes:

- Generated database roles are created from templates when database objects are
  materialized.
- Direct database user creation and role grant/revoke still act on individual
  database users.
- IdP group mappings are stored in CP for automation/playbook consumption; CP
  does not resolve IdP membership or authenticate cluster users directly.
- Repos persist metadata only. Managed-cluster SQL belongs in
  `cp/services/cluster_users.py`.

### Backups And Recovery

Use this area for backup listing, catalog sync, restore operations, and recovery
views.

| Concern | Entry points |
| --- | --- |
| API | `cp/api/clusters.py`, `cp/api/cluster_recovery.py` |
| Services | `cp/services/cluster_backups.py`, `cp/services/backup_catalog.py`, `cp/services/storage_broker.py` |
| Repos | `cp/repos/backup_catalog.py`, `cp/repos/external_connections.py` |
| Workers | `cp/workers/local/backup_catalog.py`, `cp/workers/local/restore.py` |
| Tables | `cluster_backup_catalog`, `cluster_backup_catalog_objects`, external connection tables |
| UI | Backup and Cluster Recovery sections in `webapp/index.html` and `webapp/script.js` |

### Admin Configuration

Admin configuration drives choices available to cluster operations and default
database access behavior.

| Concern | Entry points |
| --- | --- |
| API | `cp/api/admin/*.py` |
| Services | `cp/services/admin/*.py` |
| Repos | `cp/repos/admin/*.py` |
| Tables | versions, regions, disk sizes, CPU/node options, API keys, role templates, playbooks |
| UI | Admin page sections in `webapp/index.html` and `webapp/script.js` |

### Auth And Authorization

This area controls web/API authentication and CP-level visibility.

| Concern | Entry points |
| --- | --- |
| App auth wiring | `cp/auth.py` |
| Framework auth | `cpkit/cpkit/auth/*.py` |
| Services | `cp/services/auth.py` |
| Repos | `cp/repos/auth.py` |

CP-level auth determines who may use CP and what clusters they can see. Managed
cluster authentication and authorization are configured in the cluster itself and
should not be conflated with CP session auth.

### Events, Alerts, And Dashboard

| Concern | Entry points |
| --- | --- |
| Events API/service/repo | `cp/api/events.py`, `cp/services/events.py`, `cp/repos/event.py` |
| Alerts API/service/repo | `cp/api/alerts.py`, `cp/services/alerts.py`, `cp/repos/alerts.py` |
| Dashboard service | `cp/services/dashboard.py` |
| UI | Dashboard, alert, and event sections in `webapp/` |

## Common Change Starting Points

| Task | Start here |
| --- | --- |
| Add or change an API route | `cp/api/`, then matching service in `cp/services/` |
| Add a framework metadata table | `resources/cpkit_ddl.sql`, then the relevant `cpkit` package |
| Add a CP metadata table | `resources/ddl.sql`, then `cp/models.py`, then a repo method |
| Add business behavior | service file for that domain |
| Add an admin option | `cp/api/admin/`, `cp/services/admin/`, `cp/repos/admin/`, `webapp/` admin view |
| Add a webapp view | hash routing and state in `webapp/script.js`, markup in `webapp/index.html`, styles in `webapp/style.css` |
| Add a queued cluster operation | command model in `cp/models.py`, service enqueue path, worker implementation |
| Change database user or role behavior | `cp/services/cluster_users.py`, then `cp/api/clusters.py`, then Database/User Management UI |
| Change schema defaults/dev data | `resources/cpkit_ddl.sql`, `resources/ddl.sql`, `resources/init.sql`, `resources/.dev-setup.sql` |

## Naming And Documentation Conventions

- Use `database_object` for managed databases recorded by CP.
- Use `database_role_template` for admin-defined role templates.
- Use `database_role` for concrete generated roles in a cluster.
- Use `database_user` for users created or managed inside a cluster.
- Use `group_name` for IdP group identifiers stored by CP.

Good comments should explain why a block exists or which layer owns a concept.
Avoid comments that only restate the next line of code.

Recommended docstring targets:

- service methods with side effects;
- route handlers whose resource shape is not obvious;
- repo methods that intentionally return partial/lightweight models;
- helpers that translate between CP metadata and managed-cluster SQL.

## LLM Navigation Tips

When using an LLM agent on this repo, point it to this file first, then to the
domain entry points above. For bounded changes, ask it to inspect only the API,
service, repo, model, schema, and webapp files for the relevant domain before
editing.

Useful search patterns:

- `rg "database_role_group_mappings|ClusterDatabaseRole" cp webapp resources`
- `rg "CommandType|enqueue|worker" cp`
- `rg "response_model|@router" cp/api`
- `rg "x-show=\"view|setView|hash" webapp`
- `rg "CREATE TABLE public" resources/ddl.sql`
- `rg "CREATE TABLE cpkit" resources/cpkit_ddl.sql`
