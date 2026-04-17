import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

from . import DB_ENGINE, DB_URL
from .api import admin, alerts, clusters, events, jobs
from .auth import oidc
from .auth import router as auth_router
from .infra import close_db, initialize_postgres, request_id_ctx
from .workers.queue import get_nodes, pull_from_mq


@asynccontextmanager
async def lifespan(_app: FastAPI):
    queue_task: asyncio.Task | None = None

    oidc.validate_config()

    if DB_ENGINE == "postgres":
        initialize_postgres(DB_URL)
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
api.include_router(clusters.router)
api.include_router(events.router)
api.include_router(jobs.router)
# api.include_router(compute_unit.router)
# api.include_router(admin.router)


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
    # 1. Generate or capture Request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_ctx.set(request_id)

    start_time = time.perf_counter()

    # 2. Log Incoming
    logging.debug(
        f'<- {request.client[0]}:{request.client[1]} - "{request.method} {request.url.path}"'
    )

    response: Response = await call_next(request)

    # 3. Log Outgoing
    process_time_ms = (time.perf_counter() - start_time) * 1000
    logging.info(
        f'-> {request.client[0]}:{request.client[1]} - "{request.method} {request.url.path}" {response.status_code} | {process_time_ms:.2f}'
    )

    # Return ID to client so they can reference it if they have an error
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-ms"] = f"{process_time_ms:.2f}"

    return response


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
