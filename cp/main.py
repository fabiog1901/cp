"""CP FastAPI application wiring."""

import os

from cpkit import create_cpkit_app, create_cpkit_bundle
from dotenv import load_dotenv

from .api import admin, alerts, cluster_recovery, clusters, prometheus
from .models import COMMAND_MODELS, CommandType
from .repos import Repo
from .workers.commands import COMMAND_HANDLERS

load_dotenv(override=True)
DB_URL = os.getenv("DB_URL")

cpkit_capabilities = create_cpkit_bundle(
    command_models=COMMAND_MODELS,
    command_handlers=COMMAND_HANDLERS,
    reschedule_type_map={
        CommandType.CREATE_CLUSTER: CommandType.RECREATE_CLUSTER,
    },
)


app = create_cpkit_app(
    title="cp",
    version="0.1.0",
    repo_class=Repo,
    db_url=DB_URL,
    capabilities=(cpkit_capabilities,),
    routers=(
        admin.router,
        alerts.router,
        cluster_recovery.router,
        clusters.router,
        prometheus.router,
    ),
    static_directory="webapp",
    default_journald_identifier="cp",
)
