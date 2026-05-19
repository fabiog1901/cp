# Auth and Authorization

!!! note "Draft"
    This page is a human-owned domain draft. Generated route, symbol, and module
    indexes live under `docs/generated/`.

## Purpose

Auth and authorization controls who can use CP, how web sessions and API keys are
validated, and which clusters are visible to the caller.

This domain is about CP access. It is not the same as managed CockroachDB SQL
authentication or authorization.

## Concepts

- OIDC session: browser SSO session for the webapp.
- API key: direct API credential.
- Claims: identity and group data from the IdP/session.
- Access scope: CP-level group/admin visibility used to filter clusters and
  authorize actions.
- Audit actor: normalized actor id written into audit events.

## Lifecycle

1. A web user signs in through OIDC.
2. CP validates tokens and stores/reads session state.
3. API dependencies resolve the current principal.
4. Routes derive access scope from claims.
5. Services use access scope when reading or mutating cluster-related data.
6. Audit-worthy changes record the audit actor.

## Backend Entry Points

| Layer | Files |
| --- | --- |
| Auth routes | `cp/auth/router.py` |
| Dependencies | `cp/auth/dependencies.py`, `cp/auth/common.py` |
| OIDC | `cp/auth/oidc.py` |
| Services | `cp/services/auth.py`, `cp/services/admin/api_keys.py` |
| Repos | `cp/repos/auth.py`, `cp/repos/admin/api_keys.py` |

## API Resources

See [Generated API Route Index](../generated/api/routes.md) for the current
route inventory.

Important auth resources include:

- `/auth/login`
- `/auth/callback`
- `/auth/logout`
- `/auth/me`
- `/api_keys`

## Important Invariants

- CP auth controls access to CP resources.
- Managed cluster SQL auth is configured in the cluster, not enforced by the CP
  web session.
- API route handlers should use auth dependencies instead of manually parsing
  cookies or headers.
- Services should receive normalized access scope rather than raw request
  objects.
- Audit events should use the normalized audit actor.

## Do Not Confuse With

- IdP group to database role mappings are database access metadata, not CP route
  authorization rules.
- API keys authenticate direct API clients, not managed cluster SQL users.

## Common Changes

| Change | Start Here |
| --- | --- |
| Change OIDC behavior | `cp/auth/oidc.py`, `cp/auth/router.py` |
| Change route access dependencies | `cp/auth/dependencies.py`, API routes |
| Change cluster visibility | `cp/auth/common.py`, `cp/repos/cluster.py` |
| Change API keys | `cp/services/admin/api_keys.py`, `cp/repos/admin/api_keys.py` |
