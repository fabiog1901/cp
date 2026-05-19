# Database Access

!!! note "Draft"
    This page is a human-owned domain draft. Generated route, symbol, and module
    indexes live under `docs/generated/`.

## Purpose

Database access management covers CP-managed database objects, generated
database roles, database users, direct role grants, and IdP group-to-role
mappings.

This domain is intentionally split between:

- direct database user management, where CP executes SQL against the cluster;
- IdP group mappings, where CP stores desired authorization mappings for
  automation to consume.

## Concepts

- Database object: a CockroachDB database managed and tracked by CP.
- Database role template: an admin-defined SQL template used to create generated
  roles.
- Generated database role: a concrete role created for a cluster/database/schema
  from a template.
- Database user: a CockroachDB SQL user created or managed by CP.
- IdP group mapping: CP metadata that maps an external identity-provider group
  name to a generated database role.

## Lifecycle

1. An admin defines database role templates.
2. A user creates a managed database object for a cluster.
3. CP executes `CREATE DATABASE` against the cluster.
4. CP materializes generated roles from the templates.
5. A user may create database users and grant/revoke generated roles directly.
6. A user may map IdP groups to generated database roles.
7. Cluster-side authentication and authorization automation can consume those
   mappings later.

## Backend Entry Points

| Layer | Files |
| --- | --- |
| API | `cp/api/clusters.py`, `cp/api/admin/database_role_templates.py` |
| Services | `cp/services/cluster_users.py`, `cp/services/admin/cluster_options.py` |
| Repos | `cp/repos/admin/cluster_options.py` |
| Schema | `resources/ddl.sql` |
| Models | `DatabaseUser`, `ClusterDatabaseObject*`, `ClusterDatabaseRole*` in `cp/models.py` |

## Tables

| Table | Purpose |
| --- | --- |
| `database_role_templates` | Admin-defined role templates. |
| `cluster_database_objects` | Managed database objects per cluster. |
| `cluster_database_roles` | Generated database roles materialized in a cluster. |
| `cluster_database_role_group_mappings` | Desired IdP group to generated role mappings. |

## API Resources

See [Generated API Route Index](../generated/api/routes.md) for the current
route inventory.

Important database access resources include:

- `GET /clusters/{cluster_id}/database-objects`
- `POST /clusters/{cluster_id}/database-objects`
- `DELETE /clusters/{cluster_id}/database-objects/{database_name}`
- `GET /clusters/{cluster_id}/database-role-group-mappings`
- `PUT /clusters/{cluster_id}/database-role-group-mappings/{database_role}`
- `GET /clusters/{cluster_id}/users`
- `POST /clusters/{cluster_id}/users`
- direct role grant/revoke routes under `/clusters/{cluster_id}/users/{username}/...`
- admin role template routes under `/database_role_templates`

## Webapp

The main UI surfaces are:

- Database Management page: managed database cards and IdP group mapping table.
- User Management page: database users, password updates, and direct role
  grants/revokes.
- Admin page: database role template CRUD.

Relevant files:

- `webapp/index.html`
- `webapp/script.js`
- `webapp/style.css`

## Important Invariants

- CP stores IdP group mappings but does not resolve IdP group membership.
- CP web session auth is separate from managed CockroachDB SQL auth.
- Direct database user role grants are separate from IdP group mappings.
- Generated roles should come from templates and database/schema context.
- Repos persist metadata only; managed-cluster SQL belongs in
  `cp/services/cluster_users.py`.
- Dropping a database object should also remove generated role metadata through
  cascading relationships.

## Do Not Confuse With

- `database_role_template`: admin-defined template.
- `database_role`: concrete generated role in a cluster.
- `database_user`: SQL user in the managed cluster.
- `group_name`: external IdP group identifier stored by CP.

## Common Changes

| Change | Start Here |
| --- | --- |
| Change generated role creation | `cp/services/cluster_users.py` |
| Add a role template field | `resources/ddl.sql`, `cp/models.py`, admin service/repo/API |
| Change IdP mapping behavior | `cp/services/cluster_users.py`, `cp/repos/admin/cluster_options.py` |
| Change Database Management UI | `webapp/script.js`, `webapp/index.html`, `webapp/style.css` |
| Add a database access table | `resources/ddl.sql`, then model and repo |
