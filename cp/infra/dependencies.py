from cpkit.jobs import JobsService
from cpkit.playbooks import PlaybooksService
from cpkit.settings import SettingsService

from ..models import AuditEvent, CommandType, parse_command_payload
from ..services.base import log_event
from ..repository import get_repo

__all__ = [
    "get_jobs_service",
    "get_playbooks_service",
    "get_settings_service",
]


def get_jobs_service():
    return JobsService(
        get_repo(),
        parse_payload=parse_command_payload,
        reschedule_type_resolver=_resolve_reschedule_command_type,
        rescheduled_hook=log_event,
    )


def get_playbooks_service():
    return PlaybooksService(
        get_repo(),
        version_created_hook=log_event,
        version_deleted_hook=log_event,
        default_set_hook=log_event,
    )


def get_settings_service():
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
