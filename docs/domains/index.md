# Domains

Domain docs explain business behavior across CP layers. They are human-owned:
they describe purpose, invariants, workflows, and design intent. Generated facts
such as route inventories, module indexes, and Python references live under
`docs/generated/`.

Start with the domain closest to the change you are making:

- [Cluster Lifecycle](cluster-lifecycle.md)
- [Database Access](database-access.md)
- [Backups and Recovery](backups-and-recovery.md)
- [Admin Configuration](admin-configuration.md)
- [Auth and Authorization](auth-and-authorization.md)
- [Events, Alerts, and Dashboard](events-alerts-dashboard.md)

## How To Use Domain Docs

Each domain page should answer:

- what the domain owns;
- which concepts matter;
- which API, service, repo, worker, schema, and webapp files are involved;
- which invariants must not break;
- which generated docs provide the current structural facts.

When generated docs disagree with human docs, trust generated docs for facts and
update the human docs if the design intent changed.
