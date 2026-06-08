# Admin Configuration

!!! note "Draft"
    This page is a human-owned domain draft. Generated route, symbol, and module
    indexes live under `docs/generated/`.

## Purpose

Admin configuration controls the options and templates that shape cluster
creation, cluster operations, and database access defaults.

## Concepts

- Region: cloud/region/zone deployment metadata.
- Version: CockroachDB version option.
- Node count, CPU count, disk size: allowed sizing options.
- Setting: runtime CP configuration stored in metadata.
- Playbook: versioned automation content used by workers.
- API key: direct API credential.
- Database role template: SQL template used to generate concrete database roles.

## Lifecycle

1. Admins configure allowed options and templates.
2. User-facing dialogs load those options through API/service/repo layers.
3. Cluster lifecycle and database access workflows consume selected options.
4. Admin changes are audited.

## Backend Entry Points

| Layer | Files |
| --- | --- |
| API | `cp/api/admin/*.py` |
| Services | `cp/services/admin/*.py` |
| Repos | `cp/repos/admin/*.py` |
| Schema | `resources/cpkit_ddl.sql`, `resources/ddl.sql`, `resources/init.sql` |
| Models | Admin option models in `cp/models.py` |

## API Resources

See [Generated API Route Index](../generated/api/routes.md) for the current
route inventory.

Important admin resources include:

- `/versions`
- `/regions`
- `/node_counts`
- `/cpu_counts`
- `/disk_sizes`
- `/settings`
- `/playbooks`
- `/api_keys`
- `/database_role_templates`

## Webapp

Admin UI lives in the Admin page sections in:

- `webapp/index.html`
- `webapp/script.js`
- `webapp/style.css`

## Important Invariants

- Admin APIs should remain CRUD-like and delegate validation to services.
- Admin services should write audit events for user-visible changes.
- Repos should persist options only and avoid business workflows.
- Role templates are generic definitions; generated database roles are
  cluster/database-specific.
- Playbooks are operational assets and should be versioned.

## Common Changes

| Change | Start Here |
| --- | --- |
| Add a new option type | `resources/ddl.sql`, `cp/models.py`, admin repo/service/API |
| Change create-cluster options | `cp/services/cluster.py`, admin option repos |
| Change role templates | `cp/services/admin/cluster_options.py`, `cp/repos/admin/cluster_options.py` |
| Change playbook behavior | `cpkit/cpkit/playbooks/`, then CP wiring in `cp/infra/dependencies.py` if audit hooks change |
