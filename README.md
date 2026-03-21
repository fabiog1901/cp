# cp

🌍 `cp` is a control plane for CockroachDB clusters and a DBaaS-style platform for operating them safely and consistently.

It is designed to let teams create, manage, and monitor CockroachDB clusters across public clouds and, when integrated, private cloud environments too. The platform is secured through SSO login via an identity provider using OIDC, and auditable user actions are preserved internally in an event log so operational changes remain traceable over time.

At a solution level, this repository contains the application itself, but the full platform also depends on a CockroachDB cluster to store metadata and back the internal message queue, plus a Prometheus server to power dashboard queries and cluster health visibility. Integration with Alertmanager is a natural next step and is planned as a potential path for active alerting. 📈

🚀 `cp` is a Reflex-based control plane for managing CockroachDB clusters and the operational workflows around them.

It combines:

- 🖥️ a web UI built with Reflex
- 🧠 a service layer that contains business logic
- 🗄️ a repository layer for Postgres/CockroachDB access
- ⚙️ background workers that run cluster jobs through Ansible
- 🔐 SSO integration for authentication and authorization
- 📈 Prometheus-backed dashboards for cluster metrics

## 🌱 Mental Model

The project now follows a fairly clean layered shape:

1. `webapp` handles UI state, forms, routing, and page rendering.
2. `services` contain application/business logic.
3. `repos/postgres` talk to the database or external infra details.
4. `infra` contains lower-level shared infrastructure helpers.
5. `workers` execute asynchronous job workflows.

The intended direction is:

`webapp -> services -> repos -> infra`

and separately:

`workers -> repos -> infra`

This keeps the UI thin, the business rules centralized, and the persistence logic isolated.

## 🧱 Project Layout

```text
cp/
  infra/            # low-level infrastructure helpers
  repos/postgres/   # repository classes
  services/         # service classes
  webapp/           # Reflex UI
  workers/          # async/background job execution
```

Important areas:

- `cp/__init__.py`
  Registers pages, loads environment variables, and configures logging.
- `cp/webapp/pages`
  Reflex pages for admin, clusters, jobs, events, and login flows.
- `cp/webapp/state`
  Shared UI state, especially authentication/session behavior.
- `cp/services`
  Application logic like `ClusterService`, `JobsService`, `SettingsService`, and friends.
- `cp/repos/postgres`
  Database-facing repository classes like `ClusterRepo`, `JobsRepo`, `SettingsRepo`, etc.
- `cp/infra/db.py`
  Shared database execution helpers and error translation.
- `cp/workers`
  MQ polling, Ansible execution, and cluster lifecycle workflows.

## 🧭 Architecture By Layer

### 🖥️ Webapp Layer

The webapp layer should focus on:

- loading page data
- handling user interactions
- collecting form input
- showing toasts/errors
- calling service classes

It should not contain SQL, persistence logic, or non-trivial domain rules.

Examples:

- `cp/webapp/pages/clusters/clusters.py`
- `cp/webapp/pages/clusters/cluster.py`
- `cp/webapp/pages/admin/settings.py`

### 🧠 Service Layer

Services are the main home for business logic.

They now follow a class-based pattern such as:

- `ClusterService`
- `JobsService`
- `SettingsService`
- `RegionsService`
- `PlaybooksService`

Service responsibilities include:

- orchestrating multiple repos
- validating application-level rules
- translating repository failures into user-facing service errors
- shaping data for the UI

Rule of thumb:

- if the logic answers “what should happen?”, it probably belongs in a service
- if the logic answers “how do we fetch/store this?”, it probably belongs in a repo

### 🗄️ Repository Layer

Repositories are now class-based too, for example:

- `ClusterRepo`
- `JobsRepo`
- `EventRepo`
- `SettingsRepo`
- `VersionsRepo`

Repo responsibilities include:

- executing SQL
- talking to cluster databases when needed
- talking to external infra endpoints when that code is infrastructure-shaped
- returning typed models
- translating low-level failures through shared infra helpers

The repository layer should stay focused on data access and infrastructure interaction, not business orchestration.

### ⚙️ Infra Layer

`cp/infra` is the lowest-level shared foundation.

Notable examples:

- `db.py` for shared DB helpers and DB error translation
- `errors.py` for repository-level error types
- logging setup

This layer is intentionally more utility-like than object-oriented. The helpers in `db.py` are generic infrastructure functions, so keeping them as module-level functions is a good fit for now.

### 🛠️ Worker Layer

Workers handle asynchronous and operational flows.

Examples:

- consuming MQ messages
- running remote execution through Ansible
- running playbooks
- creating, scaling, upgrading, restoring, and deleting clusters

Workers usually call repos directly because they are closer to infrastructure execution than UI-driven application workflows.

## ✅ Current Conventions

After the refactor, these conventions are the preferred default:

- 📁 File names use `snake_case.py`
- 🏛️ Service modules expose a service class
- 🗃️ Repo modules expose a repo class
- 🔒 Service classes own user-facing validation and error mapping
- 🧪 Repo classes own persistence/infrastructure details
- 🧰 Infra helpers can stay as plain functions when they are generic and stateless

Examples:

- `cp/services/cluster.py` exposes `ClusterService`
- `cp/repos/postgres/cluster.py` exposes `ClusterRepo`
- `cp/repos/postgres/settings.py` exposes `SettingsRepo`

## 🔄 Typical Request Flow

A typical UI-driven flow looks like this:

1. 👤 A user clicks something in the Reflex UI.
2. 🖥️ A page/state class calls a service method.
3. 🧠 The service validates inputs and orchestrates work.
4. 🗄️ One or more repos load or persist data.
5. ⚠️ Repository errors are translated into service errors.
6. 💬 The UI shows a toast, dialog error, or updated page state.

For background operations:

1. 🧠 A service writes a job request into MQ.
2. ⚙️ A worker reads the queued message.
3. 🛠️ The worker runs the operational workflow.
4. 🗄️ Repos update jobs, tasks, events, and cluster state.

## 🧪 Error Handling Philosophy

The codebase has a layered error approach:

- repos raise repository-level errors
- services translate those into more user-appropriate service errors
- the webapp catches service errors and displays friendly messages

This is a strong pattern and worth preserving. It keeps raw infrastructure failures away from UI code and gives users more meaningful feedback. 💛

## 🚧 What Belongs Where?

When adding new code, this is the simplest guide:

- Add it to `webapp` if it is page/state/UI behavior.
- Add it to `services` if it is business logic or orchestration.
- Add it to `repos/postgres` if it is SQL or external infra access.
- Add it to `infra` if it is a generic low-level helper.
- Add it to `workers` if it belongs to async job execution.

If you are unsure between service and repo:

- choose `service` for policy, validation, orchestration
- choose `repo` for reads/writes and low-level integration

## 🔐 SSO Integration With Keycloak

Install and configure Keycloak as described in the Cockroach Labs blog post:

[CockroachDB SSO Integration Using Keycloak](https://dev.to/cockroachlabs/cockroachdb-sso-integration-using-keycloak-4b17)

The auth flow is coordinated primarily from:

- `cp/webapp/state/auth.py`
- `cp/services/auth.py`
- `cp/services/settings.py`

## 🧑‍💻 Local Development

### 1. Start CockroachDB

The cluster should have a database named `cp`.

### 2. Start Keycloak

```bash
/opt/keycloak-26.2.5/bin/kc.sh start-dev --http-port 8081 \
  --db-url-host=localhost --db-password=postgres \
  --db-username=fabio --db postgres
```

### 3. Start Prometheus

```bash
./prometheus --config.file=prometheus.yaml \
  --enable-feature=auto-reload-config \
  --config.auto-reload-interval=30s
```

### 4. Start the app

```bash
poetry shell
reflex run
```

## 📝 Notes For Future Refactors

A few follow-up ideas that may be worth exploring later:

- 🧪 introduce dependency injection only if testability or replaceable implementations start to matter more
- 📦 keep pushing for consistent naming between file names and exported classes
- 🧭 continue keeping webapp code thin and service code central
- 🧹 gradually improve docstrings and type hints in older modules

For now, the current architecture is in a much better place: clearer boundaries, cleaner naming, and a more teachable structure for new contributors. 🎉
