# CP Documentation

CP is the control plane component of a CockroachDB DBaaS platform. It provides
the API, webapp, metadata model, job framework, and operational workflows used
to create, manage, monitor, back up, and restore CockroachDB clusters.

## Start Here

- [Code Map](CODEMAP.md): the fastest route into the codebase for humans and
  coding agents.
- [Documentation System](architecture/documentation-system.md): how CP docs are
  structured for generated facts, curated intent, and LLM-assisted summaries.
- [Repository README](https://github.com/fabiog1901/cp#readme): system
  overview, architecture diagram, request flow, and high-level feature list.

## Documentation Goals

These docs are intended to work well for both humans and LLM agents:

- humans should get clear explanations and predictable navigation;
- agents should get stable maps, explicit ownership rules, and bounded entry
  points for code changes;
- domain pages should explain behavior across API, services, repos, schema,
  workers, and webapp code.

## Planned Sections

- Architecture
- Domains
- API
- Development
- Architecture decision records
- Reference
