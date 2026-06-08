"""CP FastAPI application wiring."""

from fastapi import FastAPI

from cpkit import create_cpkit_app

from . import DB_URL
from .api import admin, alerts, cluster_recovery, clusters
from .cpkit_integration import (
    auth_router,
    cpkit_admin_router,
    create_events_router,
    create_jobs_router,
    create_queue_worker,
    validate_auth_config,
)
from .prometheus import get_nodes
from .repos import Repo


def configure_api(api: FastAPI) -> None:
    @api.get("/prom-targets")
    async def get_targets():
        return get_nodes()


app = create_cpkit_app(
    title="cp",
    version="0.1.0",
    repo_class=Repo,
    db_url=DB_URL,
    routers=(
        auth_router,
        cpkit_admin_router,
        admin.router,
        alerts.router,
        cluster_recovery.router,
        clusters.router,
        create_events_router(),
        create_jobs_router(),
    ),
    configure_api=configure_api,
    startup_hooks=(validate_auth_config,),
    background_tasks=(create_queue_worker(),),
    static_directory="webapp",
    default_journald_identifier="cp",
)
