"""CP wiring for cpkit-provided capabilities."""

from cpkit import create_cpkit_admin_router
from cpkit.auth import ApiKeysService, create_auth_bundle
from cpkit.db import get_pool
from cpkit.jobs import JobsService
from cpkit.jobs import QueueMessage
from cpkit.jobs import create_jobs_router as create_cpkit_jobs_router
from cpkit.jobs import create_queue_worker as create_cpkit_queue_worker
from cpkit.playbooks import PlaybooksService
from cpkit.settings import SettingsService

from .api.admin.common import raise_http_from_service_error
from .audit import build_log_msg
from .models import AuditEvent, CommandType, parse_command_payload
from .repository import get_repo
from .services.base import log_event
from .services.errors import ServiceError
from .workers.commands import COMMAND_HANDLERS

auth = create_auth_bundle(
    get_repo=get_repo,
    audit_record_factory=build_log_msg,
)
auth_router = auth.router
oidc = auth.oidc
require_authenticated = auth.require_authenticated
require_user = auth.require_user
require_readonly = auth.require_readonly
require_admin = auth.require_admin
get_access_scope = auth.get_access_scope
get_audit_actor = auth.get_audit_actor

__all__ = [
    "auth",
    "auth_router",
    "create_admin_router",
    "create_jobs_router",
    "create_queue_worker",
    "get_access_scope",
    "get_audit_actor",
    "oidc",
    "require_admin",
    "require_authenticated",
    "require_readonly",
    "require_user",
    "validate_auth_config",
]


def validate_auth_config() -> None:
    """Validate cpkit auth settings at startup."""
    oidc.validate_config(get_repo())


def create_admin_router():
    """Create admin routes owned by cpkit and wired to CP hooks."""
    return create_cpkit_admin_router(
        get_api_keys_service=_get_api_keys_service,
        get_settings_service=_get_settings_service,
        get_playbooks_service=_get_playbooks_service,
        get_audit_actor=get_audit_actor,
        handle_service_error=raise_http_from_service_error,
        service_error_type=ServiceError,
    )


def create_jobs_router():
    """Create job management routes owned by cpkit and wired to CP hooks."""
    return create_cpkit_jobs_router(
        get_service=_get_jobs_service,
        get_access_scope=get_access_scope,
        get_audit_actor=get_audit_actor,
        require_readonly=require_readonly,
        require_user=require_user,
        handle_service_error=raise_http_from_service_error,
        service_error_type=ServiceError,
    )


def create_queue_worker():
    """Create the cpkit queue worker with CP command handlers."""
    return create_cpkit_queue_worker(
        get_pool=get_pool,
        get_repo=get_repo,
        resolve_handler=_resolve_command_handler,
        parse_message=_parse_queue_message,
    )


def _get_api_keys_service():
    return ApiKeysService(
        get_repo(),
        created_hook=log_event,
        deleted_hook=log_event,
    )


def _get_jobs_service():
    return JobsService(
        get_repo(),
        parse_payload=parse_command_payload,
        reschedule_type_resolver=_resolve_reschedule_command_type,
        rescheduled_hook=log_event,
    )


def _get_playbooks_service():
    return PlaybooksService(
        get_repo(),
        version_created_hook=log_event,
        version_deleted_hook=log_event,
        default_set_hook=log_event,
    )


def _get_settings_service():
    return SettingsService(
        get_repo(),
        setting_updated_hook=_log_setting_updated,
        setting_reset_hook=_log_setting_reset,
    )


def _log_setting_updated(repo, setting_id: str, value: str, updated_by: str) -> None:
    log_event(
        repo,
        updated_by,
        AuditEvent.SETTING_UPDATED,
        {"ID": setting_id, "value": value},
    )


def _log_setting_reset(repo, setting_id: str, updated_by: str) -> None:
    log_event(
        repo,
        updated_by,
        AuditEvent.SETTING_RESET,
        {"ID": setting_id},
    )


def _resolve_reschedule_command_type(job_type: str) -> CommandType:
    command_type = CommandType(job_type)
    if command_type == CommandType.CREATE_CLUSTER:
        return CommandType.RECREATE_CLUSTER
    return command_type


def _resolve_command_handler(message: QueueMessage):
    return COMMAND_HANDLERS.get(CommandType(message.msg_type))


def _parse_queue_message(message: QueueMessage):
    return parse_command_payload(
        CommandType(message.msg_type),
        message.msg_data,
    )
