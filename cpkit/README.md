# cpkit

FastAPI control-plane framework code extracted from `cp`.

This package owns the framework mechanics: authentication, settings, audit
recording, database helpers, error handling, and other infrastructure that every
cpkit application should get consistently. Product-specific domains, request
models, event catalogs, and lifecycle behavior stay in the applications that
consume it.

## OIDC Integration

OIDC is configured through framework settings stored in the `cpkit.settings`
table. The application supplies only the pieces cpkit cannot know:

- a repository dependency such as `get_repo`
- the session record factory used by the app repository
- secret encryption/decryption helpers
- the app role names that map to readonly, user, and admin access
- optional audit persistence for login/logout events
- the browser session cookie name, when the app wants a custom one

The integration should fit in one application-owned file:

```python
from cpkit.auth import OIDCManager, create_auth_dependencies, create_oidc_router

oidc = OIDCManager(
    encrypt_secret=encrypt_secret,
    decrypt_secret=decrypt_secret,
    session_record_factory=OIDCSessionRecord,
    session_cookie_name="cp_session",
    validate_secret_crypto_config=validate_secret_crypto_config,
)

auth = create_auth_dependencies(
    oidc,
    get_repo=get_repo,
    session_cookie_name="cp_session",
    readonly_roles=(Role.READONLY,),
    user_roles=(Role.USER, Role.ADMIN),
    admin_roles=(Role.ADMIN,),
)

router = create_oidc_router(
    oidc,
    get_repo=get_repo,
    require_authenticated=auth.require_authenticated,
    get_audit_actor=auth.get_audit_actor,
    audit_event_hook=log_auth_event,
)

require_authenticated = auth.require_authenticated
require_readonly = auth.require_readonly
require_user = auth.require_user
require_admin = auth.require_admin
get_access_scope = auth.get_access_scope
get_audit_actor = auth.get_audit_actor
```

After wiring this router into the app, cpkit handles the `/auth/login`,
`/auth/callback`, `/auth/logout`, and `/auth/me` flow, plus API-key header
authentication through `X-CP-Access-Key`, `X-CP-Signature`, and `X-Timestamp`.

## Logging Integration

Logging is provided by `cpkit.logging`. Framework settings in `cpkit.settings`
control the runtime log level and journald identifier:

- `logging.level`
- `logging.journald_identifier`

Applications should configure logging and install the request logging middleware
through the cpkit API:

```python
from cpkit.logging import configure_logging, request_logging_middleware

configure_logging(get_repo(), force=True, default_journald_identifier="cp")


@app.middleware("http")
async def dispatch(request, call_next):
    return await request_logging_middleware(request, call_next)
```

`request_logging_middleware` manages the request id context, emits inbound and
outbound request logs, and adds `X-Request-ID` plus `X-Process-Time-ms` response
headers.

## Jobs Integration

The framework owns the durable message queue and worker polling loop. The queue
table lives in `cpkit.mq`; applications enqueue messages through
`QueueRepositoryMixin` and run workers through `run_queue_worker`.

Applications still own business job semantics:

- command enums and payload models
- command parsing
- handler functions
- application job/task metadata
- failure bookkeeping

```python
from cpkit.jobs import QueueMessage, QueueRepositoryMixin, run_queue_worker


class Repo(QueueRepositoryMixin, ...):
    ...


async def pull_from_queue():
    await run_queue_worker(
        get_pool=get_pool,
        resolve_handler=resolve_handler,
        parse_message=parse_message,
        handle_failure=handle_failure,
    )
```

This keeps queue claiming, dispatch, deletion, polling jitter, and cancellation
handling in cpkit while leaving job behavior to the consuming app.
