"""CP FastAPI application wiring."""

from fastapi import FastAPI

from cpkit import create_cpkit_app
from cpkit.jobs import create_jobs_router

from . import DB_URL
from .api import admin, alerts, cluster_recovery, clusters, events
from .api.admin.common import raise_http_from_service_error
from .auth import (
    get_access_scope,
    get_audit_actor,
    oidc,
    require_readonly,
    require_user,
)
from .auth import router as auth_router
from .infra import get_jobs_service
from .repository import get_repo
from .services.errors import ServiceError
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
        create_jobs_router(
            get_service=get_jobs_service,
            get_access_scope=get_access_scope,
            get_audit_actor=get_audit_actor,
            require_readonly=require_readonly,
            require_user=require_user,
            handle_service_error=raise_http_from_service_error,
            service_error_type=ServiceError,
        ),
    ),
    configure_api=configure_api,
    startup_hooks=(validate_oidc_config,),
    background_tasks=(pull_from_mq,),
    static_directory="webapp",
    default_journald_identifier="cp",
)
