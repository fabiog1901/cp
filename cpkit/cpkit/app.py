"""FastAPI application bootstrap helpers."""

import asyncio
import inspect
from collections.abc import Awaitable, Callable, Iterable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.staticfiles import StaticFiles

from cpkit.db import close_db, initialize_postgres
from cpkit.logging import configure_logging, request_logging_middleware

StartupHook = Callable[[], Any]
BackgroundTaskFactory = Callable[[], Awaitable[Any]]
ConfigureApi = Callable[[FastAPI], None]


def create_cpkit_app(
    *,
    title: str,
    version: str,
    get_repo: Callable[[], Any],
    db_url: str | None,
    routers: Iterable[APIRouter] = (),
    configure_api: ConfigureApi | None = None,
    startup_hooks: Iterable[StartupHook] = (),
    background_tasks: Iterable[BackgroundTaskFactory] = (),
    static_directory: str | Path | None = None,
    api_prefix: str = "/api",
    default_journald_identifier: str = "cp",
) -> FastAPI:
    """Create a cpkit-managed FastAPI app with an application API subapp."""

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        running_tasks: list[asyncio.Task[Any]] = []

        initialize_postgres(db_url)
        repo = get_repo()
        configure_logging(
            repo,
            force=True,
            default_journald_identifier=default_journald_identifier,
        )
        for hook in startup_hooks:
            result = hook()
            if inspect.isawaitable(result):
                await result

        running_tasks = [
            asyncio.create_task(task_factory())
            for task_factory in background_tasks
        ]

        yield

        for task in running_tasks:
            task.cancel()
        for task in running_tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass

        close_db()

    app = FastAPI(lifespan=lifespan)
    api = FastAPI(title=title, version=version)

    for router in routers:
        api.include_router(router)

    if configure_api is not None:
        configure_api(api)

    app.mount(api_prefix, api)

    if static_directory is not None:
        app.mount(
            "/",
            StaticFiles(directory=Path(static_directory), html=True),
            name="webapp",
        )

    @app.middleware("http")
    async def dispatch(request: Request, call_next):
        return await request_logging_middleware(request, call_next)

    return app
