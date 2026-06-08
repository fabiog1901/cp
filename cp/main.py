"""CP FastAPI application wiring."""

from fastapi import FastAPI

from cpkit import create_cpkit_app, create_cpkit_bundle

from . import DB_URL
from .api import admin, alerts, cluster_recovery, clusters
from .audit import build_log_msg
from .models import CommandType, parse_command_payload
from .prometheus import get_nodes
from .repos import Repo
from .workers.commands import COMMAND_HANDLERS

cpkit_bundle = create_cpkit_bundle(
    audit_record_factory=build_log_msg,
    parse_job_payload=lambda command_type, payload: parse_command_payload(
        CommandType(command_type),
        payload,
    ),
    reschedule_type_map={
        CommandType.CREATE_CLUSTER: CommandType.RECREATE_CLUSTER,
    },
    resolve_queue_handler=lambda message: COMMAND_HANDLERS.get(
        CommandType(message.msg_type)
    ),
    parse_queue_message=lambda message: parse_command_payload(
        CommandType(message.msg_type),
        message.msg_data,
    ),
)


def configure_api(api: FastAPI) -> None:
    @api.get("/prom-targets")
    async def get_targets():
        return get_nodes()


app = create_cpkit_app(
    title="cp",
    version="0.1.0",
    repo_class=Repo,
    db_url=DB_URL,
    bundles=(cpkit_bundle,),
    routers=(
        admin.router,
        alerts.router,
        cluster_recovery.router,
        clusters.router,
    ),
    configure_api=configure_api,
    static_directory="webapp",
    default_journald_identifier="cp",
)
