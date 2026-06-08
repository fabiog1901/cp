# Documentation System

CP documentation follows one rule:

> Facts are generated. Intent is curated. Summaries are synthesized.

The goal is to keep documentation useful for humans and LLM agents without
making humans manually maintain facts that can be extracted from code.

## Goals

The documentation system should:

- treat source code as the primary source of truth;
- derive structural documentation from code where possible;
- let LLMs summarize and connect information, not infer structure from scratch;
- keep generated docs deterministic;
- reserve human-authored docs for intent, architecture, invariants, and design
  rationale.

## Canonical Sources

Developers maintain:

- source code;
- tests;
- type hints;
- docstrings;
- module headers;
- architecture and invariant docs;
- design rationale and ADRs.

LLMs may help draft these artifacts, but developers are the final authority.

## Pipeline

```text
Python code
    ↓
AST + filesystem scanning
    ↓
tools/docsync.py
    ↓
structured metadata index
    ↓
generated Markdown docs
    ↓
LLM summarization pass
    ↓
MkDocs site
    ↓
GitHub Pages
```

## Responsibilities

### Developers Own

- code correctness;
- tests;
- docstrings;
- architectural intent;
- invariants;
- design rationale.

### `tools/docsync.py` Owns

Deterministic extraction:

- filesystem structure;
- package and module inventory;
- class and function extraction;
- signatures;
- docstrings;
- imports and dependency hints;
- public APIs;
- route/task/command indexes;
- navigation metadata;
- stale-doc detection.

### LLMs Own

Semantic summarization:

- package overviews;
- navigation hints;
- onboarding docs;
- edit guidance;
- human-readable summaries;
- cross-linking assistance.

LLMs should use generated indexes, docstrings, package metadata, and architecture
docs instead of traversing the entire repository when a bounded source exists.

## Repository Layout

The target documentation layout is:

```text
docs/
  index.md
  CODEMAP.md
  generated/
    code-map.md
    package-index.md
    api/
    llm-index.md
  architecture/
  guides/
  concepts/
  domains/
  development/
  adr/
  reference/
tools/
  docsync.py
.build/
  project-index.json
mkdocs.yml
```

Generated files must start with:

```md
<!-- GENERATED FILE: DO NOT EDIT -->
```

Generated files should not be manually edited.

## Generated Docs

Generated docs answer:

- What exists?
- Where is it?
- What depends on what?
- Which APIs are available?
- Which symbols, routes, commands, or workers are public entry points?

Planned generated files:

- `docs/generated/code-map.md`
- `docs/generated/package-index.md`
- `docs/generated/api/*.md`
- `docs/generated/llm-index.md`
- `.build/project-index.json`

The JSON index is the machine-readable map that agents should prefer over
full-repository traversal.

## Human Docs

Human-authored docs answer:

- Why is it designed this way?
- Which invariants matter?
- What must not break?
- Which architectural constraints apply?
- Which workflows should contributors follow?

Human-owned sections include:

- `docs/architecture/`
- `docs/domains/`
- `docs/guides/`
- `docs/concepts/`
- `docs/development/`
- `docs/adr/`
- `docs/reference/`

## Stale Documentation Detection

`tools/docsync.py` should eventually support a mapping from code paths to
human-authored docs that may need review when code changes.

Example shape:

```yaml
packages:
  database_access:
    paths:
      - cp/services/cluster_users.py
      - cp/api/clusters.py
      - cp/repos/admin/cluster_options.py
      - resources/cpkit_ddl.sql
      - resources/ddl.sql
    review:
      - docs/domains/database-access.md
      - docs/adr/0002-idp-group-role-mappings.md
```

On pull requests, the check mode should flag potentially stale docs without
trying to rewrite human-authored intent.

## CI Expectations

The intended CI commands are:

```bash
python tools/docsync.py --check
mkdocs build --strict
```

Optional local regeneration:

```bash
python tools/docsync.py --write
```

Checks should eventually include:

- generated docs are up to date;
- `.build/project-index.json` is current;
- public APIs have docstrings;
- package READMEs exist;
- human docs affected by code changes are flagged for review.

## MkDocs Role

MkDocs is the unified publishing layer for both human and agent-friendly docs.
Markdown remains simple enough for LLMs to parse, while MkDocs Material provides
navigation, search, and GitHub Pages publishing.

The generated documentation should be included in the MkDocs nav once
`tools/docsync.py` exists and can produce those files deterministically.

## Design Principles

- Keep facts close to code and generate them.
- Keep intent in curated Markdown.
- Keep summaries reproducible by grounding them in generated metadata and
  docstrings.
- Avoid separate "human docs" and "LLM docs"; maintain one documentation system
  with predictable structure.
- Prefer small, linked pages over giant mixed-purpose pages.
