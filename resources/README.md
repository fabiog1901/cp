# Resources

This directory contains schema, seed, development, and example automation files.

For the broader map, see [`../docs/CODEMAP.md`](../docs/CODEMAP.md).

## Entry Points

| File or directory | Purpose |
| --- | --- |
| `../cpkit/resources/ddl.sql` | Framework-owned schema and tables. Run before CP schema setup. |
| `ddl.sql` | Canonical CP metadata schema for public-schema application tables. |
| `init.sql` | Initial/default data loaded with the schema. |
| `post_schema.sql` | SQL that runs after the main schema setup. |
| `.dev-setup.sql` | Local development setup helpers. |
| `playbook_examples/` | Example command payloads/playbooks for cluster operations. |

## Common Pattern

When adding a persisted feature:

1. Add or modify framework tables in `../cpkit/resources/ddl.sql`, or CP application tables in `ddl.sql`.
2. Add seed/default rows to `init.sql` only when the application needs them.
3. Add or update Pydantic models in `cp/models.py` or the relevant `cpkit`
   package for framework-owned tables.
4. Add repository methods for the new table.
5. Wire service/API/webapp behavior as needed.

Keep schema names aligned with the domain language used in `docs/CODEMAP.md`.
