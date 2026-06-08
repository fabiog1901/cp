"""CP FastAPI application wiring."""

from fastapi import FastAPI

from cpkit import create_cpkit_app

from . import DB_URL
from .api import admin, alerts, cluster_recovery, clusters, events, jobs
from .auth import oidc
from .auth import router as auth_router
from .repository import get_repo
from .workers.queue import get_nodes, pull_from_mq


def configure_api(api: FastAPI) -> None:
    @api.get("/prom-targets")
    async def get_targets():
        return get_nodes()


def validate_oidc_config() -> None:
    oidc.validate_config(get_repo())


app = create_cpkit_app(
    title="cp",
    version="0.1.0",
    get_repo=get_repo,
    db_url=DB_URL,
    routers=(
        auth_router,
        admin.router,
        alerts.router,
        cluster_recovery.router,
        clusters.router,
        events.router,
        jobs.router,
    ),
    configure_api=configure_api,
    startup_hooks=(validate_oidc_config,),
    background_tasks=(pull_from_mq,),
    static_directory="webapp",
    default_journald_identifier="cp",
)
