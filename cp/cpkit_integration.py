"""CP callbacks and auth dependencies supplied to cpkit."""

from cpkit import create_cpkit_bundle

from .audit import build_log_msg
from .models import CommandType, parse_command_payload
from .services.base import log_event
from .workers.commands import COMMAND_HANDLERS

CREATE_CLUSTER = CommandType.CREATE_CLUSTER
RECREATE_CLUSTER = CommandType.RECREATE_CLUSTER

cpkit_bundle = create_cpkit_bundle(
    audit_record_factory=build_log_msg,
    audit_event_hook=log_event,
    parse_job_payload=lambda command_type, payload: parse_command_payload(
        CommandType(command_type),
        payload,
    ),
    reschedule_type_resolver=lambda job_type: (
        RECREATE_CLUSTER
        if CommandType(job_type) == CREATE_CLUSTER
        else CommandType(job_type)
    ),
    resolve_queue_handler=lambda message: COMMAND_HANDLERS.get(
        CommandType(message.msg_type)
    ),
    parse_queue_message=lambda message: parse_command_payload(
        CommandType(message.msg_type),
        message.msg_data,
    ),
)

require_authenticated = cpkit_bundle.require_authenticated
require_user = cpkit_bundle.require_user
require_readonly = cpkit_bundle.require_readonly
require_admin = cpkit_bundle.require_admin
get_access_scope = cpkit_bundle.get_access_scope
get_audit_actor = cpkit_bundle.get_audit_actor

__all__ = [
    "cpkit_bundle",
    "get_access_scope",
    "get_audit_actor",
    "require_admin",
    "require_authenticated",
    "require_readonly",
    "require_user",
]
