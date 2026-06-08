"""FastAPI application entry point.

This module wires routers, middleware, startup/shutdown behavior, static webapp
serving, request IDs, and top-level exception handling.
"""

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from cpkit.logging import configure_logging, request_logging_middleware

from . import DB_ENGINE, DB_URL
from .api import admin, alerts, cluster_recovery, clusters, events, jobs
from .auth import oidc
from .auth import router as auth_router
from .infra import close_db, get_repo, initialize_postgres
from .workers.queue import get_nodes, pull_from_mq


@asynccontextmanager
async def lifespan(_app: FastAPI):
    queue_task: asyncio.Task | None = None

    if DB_ENGINE == "postgres":
        initialize_postgres(DB_URL)
        configure_logging(get_repo(), force=True, default_journald_identifier="cp")
        oidc.validate_config(get_repo())
        queue_task = asyncio.create_task(pull_from_mq())
    else:
        pass

    yield

    if queue_task is not None:
        queue_task.cancel()
        try:
            await queue_task
        except asyncio.CancelledError:
            pass

    close_db()


app = FastAPI(lifespan=lifespan)

api = FastAPI(
    title="cp",
    version="0.1.0",
)

# all API endpoints are grouped in dedicated routers
api.include_router(auth_router)
api.include_router(admin.router)
api.include_router(alerts.router)
api.include_router(cluster_recovery.router)
api.include_router(clusters.router)
api.include_router(events.router)
api.include_router(jobs.router)


@api.get("/prom-targets")
async def get_targets():
    return get_nodes()


app.mount("/api", api)
app.mount(
    "/",
    StaticFiles(directory=Path("webapp"), html=True),
    name="webapp",
)


@app.middleware("http")
async def dispatch(request: Request, call_next):
    return await request_logging_middleware(request, call_next)


# SPA fallback: any non-/api path returns index.html
# @app.get(
#     "/{full_path:path}",
#     include_in_schema=False,
# )
# def webapp_fallback(request: Request, full_path: str):
#     # don't intercept API paths (mounted apps usually handle this, but keep it explicit if needed)
#     if full_path.startswith("api/"):
#         return {"detail": "Not Found"}

#     return FileResponse(WEBAPP / "index.html")
